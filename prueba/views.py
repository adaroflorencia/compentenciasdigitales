import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Question, Option, TopicResult

def docente(request):
    return render(request, 'form/docentes.html')

def estudiante(request):
    return render(request, 'form/estudiantes.html')

def obtener_preguntas_por_rol(usuario):
    try:
        if not usuario.rol:
            logging.warning(f"El usuario {usuario.email} no tiene un rol asignado")
            return Question.objects.none()

        if usuario.rol.nombre == 'administrador':
            preguntas = Question.objects.all()
            return preguntas

        tema = Topic.objects.filter(rol=usuario.rol)

        if not tema.exists():
            logging.warning(f"No se encontró ningún tema para el rol {usuario.rol.nombre}")
            return Question.objects.none()

        preguntas = Question.objects.filter(tema__in=tema)

        return preguntas

    except Exception as e:
        logging.error(f"Error al obtener preguntas para el usuario {usuario.email}: {e}")
        return Question.objects.none()


@login_required
def evaluar(request):
    # Si ya completó el formulario, redirigir a resultados
    if TopicResult.objects.filter(usuario=request.user).exists():
        return redirect('resultados')

    # Obtener todas las preguntas solo si no están en la sesión
    if 'todas_las_preguntas' not in request.session:
        todas_las_preguntas = list(obtener_preguntas_por_rol(request.user))
        # Guardar los IDs de las preguntas en la sesión
        request.session['todas_las_preguntas'] = [q.id for q in todas_las_preguntas]
    else:
        # Recuperar las preguntas usando los IDs guardados
        ids_preguntas = request.session['todas_las_preguntas']
        todas_las_preguntas = list(Question.objects.filter(id__in=ids_preguntas))

    # Inicializar variables de sesión si no existen
    if 'respuestas' not in request.session:
        request.session['respuestas'] = {}
    if 'pregunta_actual' not in request.session:
        request.session['pregunta_actual'] = 0
    if 'puntajes_tema' not in request.session:
        request.session['puntajes_tema'] = {}
    if 'preguntas_acumuladas' not in request.session:
        request.session['preguntas_acumuladas'] = []
    if 'puntaje_total' not in request.session:
        request.session['puntaje_total'] = 0

    indice_pregunta_actual = request.session['pregunta_actual']

    # Si es la última pregunta y ya fue respondida, ir a resultados
    if indice_pregunta_actual >= len(todas_las_preguntas):
        request.session['formulario_completado'] = True
        return redirect('resultados')

    pregunta_actual = todas_las_preguntas[indice_pregunta_actual]
    tema_actual = pregunta_actual.tema
    opciones = Option.objects.filter(pregunta=pregunta_actual)

    if request.method == 'POST':
        opcion_seleccionada = request.POST.get('opcion')

        if opcion_seleccionada:
            try:
                opcion = Option.objects.get(id=opcion_seleccionada)

                # Guardar la respuesta
                respuestas = request.session['respuestas']
                respuestas[str(pregunta_actual.id)] = opcion_seleccionada
                request.session['respuestas'] = respuestas

                # Actualizar puntaje solo si la pregunta no ha sido respondida antes
                preguntas_acumuladas = request.session['preguntas_acumuladas']
                if str(pregunta_actual.id) not in preguntas_acumuladas:
                    request.session['puntaje_total'] += opcion.puntaje
                    preguntas_acumuladas.append(str(pregunta_actual.id))
                    request.session['preguntas_acumuladas'] = preguntas_acumuladas

                    puntajes_tema = request.session['puntajes_tema']
                    nombre_tema = tema_actual.nombre
                    puntajes_tema[nombre_tema] = puntajes_tema.get(nombre_tema, 0) + opcion.puntaje
                    request.session['puntajes_tema'] = puntajes_tema

                # Si se presiona el botón de finalizar en la última pregunta
                if 'finalizar' in request.POST and indice_pregunta_actual == len(todas_las_preguntas) - 1:
                    request.session['formulario_completado'] = True
                    request.session.modified = True
                    return redirect('resultados')

            except Option.DoesNotExist:
                logging.error(f"Opción con ID {opcion_seleccionada} no encontrada")

        # Procesar navegación
        if 'siguiente' in request.POST:
            request.session['pregunta_actual'] += 1
        elif 'anterior' in request.POST:
            request.session['pregunta_actual'] = max(0, request.session['pregunta_actual'] - 1)

        request.session.modified = True
        return redirect('evaluar')

    # Recuperar respuesta guardada
    respuesta_guardada = request.session['respuestas'].get(str(pregunta_actual.id), '')

    # Calcular progreso
    progreso = int((indice_pregunta_actual / len(todas_las_preguntas)) * 100) if todas_las_preguntas else 0

    contexto = {
        'pregunta': pregunta_actual,
        'tema': tema_actual,
        'opciones': opciones,
        'progreso': progreso,
        'respuesta_guardada': respuesta_guardada,
        'tiene_anterior': indice_pregunta_actual > 0,
        'tiene_siguiente': indice_pregunta_actual < len(todas_las_preguntas) - 1,
        'puntajes_tema': request.session.get('puntajes_tema', {}),
        'indice_actual': indice_pregunta_actual + 1,
        'total_preguntas': len(todas_las_preguntas)
    }

    return render(request, 'form/evaluar.html', contexto)

@login_required
def resultados(request):
    try:
        # Verificar si ya existen resultados en la base de datos
        resultados_existentes = TopicResult.objects.filter(usuario=request.user)

        if resultados_existentes.exists():
            # Devolver los resultados existentes desde la base de datos
            resultados_finales = {}
            puntaje_total = 0
            total_preguntas = 0

            for resultado in resultados_existentes:
                porcentaje_puntaje = resultado.puntaje
                resultados_finales[resultado.tema.nombre] = {
                    'puntaje': (porcentaje_puntaje * 100) / 6,
                    'total_preguntas': resultado.total_preguntas,
                    'preguntas_respondidas': resultado.total_preguntas,
                    'nivel': resultado.nivel
                }
                puntaje_total += resultado.puntaje
                total_preguntas += 1

            promedio_total = round(puntaje_total / total_preguntas, 2) if total_preguntas > 0 else 0

        else:
            # Verificar si el formulario está completado y los resultados deben guardarse
            if not request.session.get('formulario_completado'):
                return redirect('evaluar')

            puntajes_tema = request.session.get('puntajes_tema')
            if not puntajes_tema:
                return redirect('evaluar')

            # Calcular y guardar resultados solo si no han sido guardados antes
            preguntas = obtener_preguntas_por_rol(request.user)
            preguntas_por_tema = {}
            resultados_finales = {}

            for pregunta in preguntas:
                if pregunta.tema not in preguntas_por_tema:
                    preguntas_por_tema[pregunta.tema] = []
                preguntas_por_tema[pregunta.tema].append(pregunta)

            preguntas_acumuladas = request.session.get('preguntas_acumuladas', [])
            total_preguntas_respondidas = len(preguntas_acumuladas)
            puntaje_total = request.session.get('puntaje_total', 0)

            for tema, lista_preguntas in preguntas_por_tema.items():
                if tema.nombre in puntajes_tema:
                    preguntas_respondidas = len([q.id for q in lista_preguntas if str(q.id) in preguntas_acumuladas])

                    if preguntas_respondidas > 0:
                        puntaje_promedio = (puntajes_tema[tema.nombre] * 100) / (preguntas_respondidas * 6)
                        nivel = determinar_nivel(puntaje_promedio)

                        # Guardar resultados en la base de datos
                        TopicResult.objects.create(
                            tema=tema,
                            usuario=request.user,
                            puntaje=round(puntaje_promedio, 2),
                            nivel=nivel,
                            total_preguntas=len(lista_preguntas)
                        )

                        resultados_finales[tema.nombre] = {
                            'puntaje': round(puntaje_promedio, 2),
                            'total_preguntas': len(lista_preguntas),
                            'preguntas_respondidas': preguntas_respondidas,
                            'nivel': nivel
                        }

            promedio_total = round(puntaje_total / total_preguntas_respondidas, 2) if total_preguntas_respondidas > 0 else 0

            # Limpiar la sesión después de guardar los resultados
            claves_sesion = ['respuestas', 'pregunta_actual', 'puntajes_tema',
                             'preguntas_acumuladas', 'puntaje_total', 'todas_las_preguntas', 'formulario_completado']
            for clave in claves_sesion:
                if clave in request.session:
                    del request.session[clave]

        nivel_total = determinar_nivel(promedio_total)

        return render(request, 'form/resultados.html', {
            'resultados': resultados_finales,
            'puntaje_total': promedio_total,
            'rol_usuario': request.user.rol.nombre if request.user.rol else None,
            'nivel_total': nivel_total,
        })

    except Exception as e:
        logging.error(f"Error procesando resultados para usuario {request.user.email}: {e}")
        if TopicResult.objects.filter(usuario=request.user).exists():
            return redirect('resultados')
        return redirect('evaluar')


def determinar_nivel(puntaje):
    if 0 <= puntaje < 2 :
        return 'A1'
    elif puntaje < 3:
        return 'A2'
    elif puntaje < 4:
        return 'B1'
    elif puntaje < 5:
        return 'B2'
    elif puntaje < 6:
        return 'C1'
    else:
        return 'C2'


@login_required
def enviar_respuestas(request):
    try:
        if not request.session.get('respuestas'):
            return redirect('evaluar.html')

        return redirect('resultados.html')

    except Exception as e:
        logging.error(f"Error en enviar_respuestas: {e}")
        return redirect('resultados.html')
