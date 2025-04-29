from flask import Flask, render_template, url_for
import sys
import os
import traceback # Importa traceback para errores detallados

# Añadir el directorio 'modules' al path... (código existente)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

try:
    from exercise_generator import generate_combined_exercise
    generator_imported = True
except ImportError as e:
    print(f"ERROR: No se pudo importar 'generate_combined_exercise': {e}")
    print(traceback.format_exc()) # Imprime el stack trace completo
    generator_imported = False
    # Define una función dummy si la importación falla, para que Flask no se caiga
    def generate_combined_exercise(*args, **kwargs):
        return {
            "problem_latex": r"\text{Error al importar el generador}",
            "solution_latex": r"\text{Revisa la consola de Flask}",
            "problem_sympy": None,
            "solution_sympy": None
        }


app = Flask(__name__)

@app.route('/')
def index():
    print("--- Accediendo a la ruta / ---") # Mensaje de depuración
    exercise_data = None # Inicializa por si falla la generación
    try:
        if generator_imported:
            print("Llamando a generate_combined_exercise...") # Mensaje de depuración
            exercise_data = generate_combined_exercise(num_fractions=2, max_degree=1)
            print(f"Datos del ejercicio generados: {exercise_data}") # <<< ¡IMPORTANTE! Mira este output
        else:
            print("Usando datos de error porque el generador no se importó.")
            exercise_data = generate_combined_exercise() # Llama a la versión dummy

        if not isinstance(exercise_data, dict) or 'problem_latex' not in exercise_data:
            print("¡ALERTA! exercise_data no es un diccionario válido o le falta 'problem_latex'")
            # Proporciona datos de error si la generación falló o devolvió algo inesperado
            exercise_data = {
                "problem_latex": r"\text{Error en la generación del ejercicio}",
                "solution_latex": r"\text{Revisa la consola de Flask}",
            }

    except Exception as e:
        print(f"¡ERROR al generar el ejercicio dentro de la ruta!: {e}")
        print(traceback.format_exc()) # Imprime el stack trace completo del error
        exercise_data = {
            "problem_latex": r"\text{Excepción durante la generación}",
            "solution_latex": f"Error: {e}",
        }

    print(f"Renderizando index.html con exercise_data: {exercise_data}") # Mensaje de depuración
    return render_template('index.html', exercise=exercise_data)

if __name__ == '__main__':
    # Asegúrate de que el import funcionó antes de intentar ejecutar
    if not generator_imported:
         print("\n!!! No se pudo importar el generador. La aplicación se ejecutará pero mostrará errores. !!!\n")
    app.run(debug=True)
