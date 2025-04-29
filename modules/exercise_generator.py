import random
import sympy

# Define la variable simbólica principal (puedes añadir más si quieres)
x = sympy.symbols('x')

def _generate_polynomial(degree=1, min_coef=-5, max_coef=5, ensure_variable=True):
    """Genera un polinomio simple de un grado específico."""
    if degree < 0:
        degree = 0
    coeffs = [random.randint(min_coef, max_coef) for _ in range(degree + 1)]

    # Asegurarse de que el coeficiente de mayor grado no sea cero si degree > 0
    if degree > 0 and coeffs[0] == 0:
        coeffs[0] = random.choice([c for c in range(min_coef, max_coef + 1) if c != 0] or [1])

    # Asegurarse de que la variable esté presente si ensure_variable es True y degree > 0
    if ensure_variable and degree > 0 and all(c == 0 for c in coeffs[:-1]):
         # Si todos los coeficientes de x son 0, forzamos uno a no serlo
        idx_to_change = random.randint(0, degree -1)
        coeffs[idx_to_change] = random.choice([c for c in range(min_coef, max_coef + 1) if c != 0] or [1])

     # Asegurarse de que el polinomio no sea simplemente 0 (a menos que degree sea 0 y el coef sea 0)
    if all(c == 0 for c in coeffs) and (degree > 0 or coeffs[0] != 0) :
         coeffs[random.randint(0, degree)] = random.choice([c for c in range(min_coef, max_coef + 1) if c != 0] or [1])


    poly = sum(c * x** (degree - i) for i, c in enumerate(coeffs))
    return poly

def _generate_fraction(max_degree_num=1, max_degree_den=1):
    """Genera una fracción algebraica asegurándose que el denominador no sea cero."""
    num = _generate_polynomial(degree=random.randint(0, max_degree_num))
    den = sympy.Integer(0)
    # Asegurar que el denominador no sea el polinomio cero
    while den.is_zero:
        den = _generate_polynomial(degree=random.randint(0, max_degree_den), ensure_variable=True)
        # Opcional: Evitar denominadores constantes (excepto 1 o -1) para más interés
        if den.is_constant() and den != 1 and den != -1:
             den = sympy.Integer(0) # Forza a regenerar

    # Simplificación inicial leve para evitar casos triviales obvios como (2x+2)/(2) -> x+1
    fraction = sympy.cancel(num / den)
    return fraction


def generate_combined_exercise(num_fractions=2, max_degree=1, operations=None):
    """
    Genera un ejercicio de operaciones combinadas con fracciones algebraicas.
    """
    if operations is None:
        operations = [sympy.Add, sympy.Mul, sympy.Add, sympy.Mul, sympy.Add, sympy.Mul, sympy.Pow] # +, *, / (representado por Pow con -1)
        # Ajusta la probabilidad de cada operación si quieres

    fractions = [_generate_fraction(max_degree, max_degree) for _ in range(num_fractions)]

    # Construir la expresión
    exercise_expr = fractions[0]
    ops_symbols = []

    for i in range(1, num_fractions):
        op_class = random.choice(operations)
        op_symbol = "?" # Placeholder

        if op_class == sympy.Add:
            # Decide aleatoriamente entre suma y resta
            if random.choice([True, False]):
                exercise_expr += fractions[i]
                op_symbol = "+"
            else:
                # Evitar resta si la fracción es negativa para no tener --
                if fractions[i].could_extract_minus_sign():
                     exercise_expr += fractions[i] # Se convierte en suma
                     op_symbol = "+"
                else:
                     exercise_expr -= fractions[i]
                     op_symbol = "-"
        elif op_class == sympy.Mul:
            exercise_expr *= fractions[i]
            op_symbol = r"\cdot" # Símbolo de multiplicación para LaTeX
        elif op_class == sympy.Pow: # Usamos Pow con exponente -1 para representar división
             # Asegurarse de que la fracción a dividir no sea cero
             if fractions[i].is_zero:
                 # Si es cero, cambia la operación a suma o multiplicación
                 if random.choice([True, False]):
                      exercise_expr += fractions[i] # Se vuelve 0, ejercicio simple
                      op_symbol = "+"
                 else:
                      exercise_expr *= fractions[i] # Se vuelve 0, ejercicio simple
                      op_symbol = r"\cdot"
             else:
                exercise_expr /= fractions[i]
                op_symbol = ":" # Símbolo de división para LaTeX

        ops_symbols.append(op_symbol)


    # Generar la representación LaTeX del problema
    # Itera para construir el string LaTeX manualmente para mostrar las operaciones originales
    problem_latex = sympy.latex(fractions[0], mode='plain')
    for i in range(num_fractions - 1):
        problem_latex += f" {ops_symbols[i]} {sympy.latex(fractions[i+1], mode='plain')}"

    # Simplificar la expresión para obtener la solución
    # Usar together() o cancel() para simplificar la suma/resta/division de fracciones
    try:
        # solution_expr = sympy.simplify(exercise_expr) # simplify puede ser muy agresivo a veces
        solution_expr = sympy.cancel(exercise_expr) # cancel es bueno para fracciones
        # solution_expr = sympy.together(exercise_expr) # together combina sobre un denominador común
    except Exception as e:
        print(f"Error during simplification: {e}")
        # Si falla la simplificación, usa la expresión sin simplificar como 'solución'
        solution_expr = exercise_expr


    solution_latex = sympy.latex(solution_expr, mode='plain')

    return {
        "problem_latex": problem_latex + " =",
        "solution_latex": solution_latex,
        "problem_sympy": exercise_expr, # Objeto sympy original (útil para debugging)
        "solution_sympy": solution_expr # Objeto sympy simplificado
    }

# Ejemplo de uso (para probar el módulo directamente)
if __name__ == "__main__":
    for i in range(5):
        exercise = generate_combined_exercise(num_fractions=random.randint(2, 3), max_degree=1)
        print(f"Problema {i+1}: {exercise['problem_latex']}")
        print(f"Solución {i+1}: {exercise['solution_latex']}")
        print("-" * 20)

    print("\nEjercicio con mayor grado:")
    exercise_deg2 = generate_combined_exercise(num_fractions=2, max_degree=2)
    print(f"Problema: {exercise_deg2['problem_latex']}")
    print(f"Solución: {exercise_deg2['solution_latex']}")

