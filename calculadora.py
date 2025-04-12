import sys
import re
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.integrate import solve_ivp
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, 
                             QLabel, QTabWidget, QMessageBox, QTextEdit, QComboBox)
from PyQt6.QtGui import QAction
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class DerivativeCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Derivadas y EDOs")
        self.setGeometry(100, 100, 900, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.main_layout.addWidget(self.left_panel, 1)  # Ocupa la mitad izquierda

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.main_layout.addWidget(self.right_panel, 1)  # Ocupa la mitad derecha

        self.tabs = QTabWidget()
        self.left_layout.addWidget(self.tabs)

        self.derivative_tab = QWidget()
        self.derivative_layout = QVBoxLayout()
        self.derivative_tab.setLayout(self.derivative_layout)
        self.tabs.addTab(self.derivative_tab, "Derivadas")

        self.ode_tab = QWidget()
        self.ode_layout = QVBoxLayout()
        self.ode_tab.setLayout(self.ode_layout)
        self.tabs.addTab(self.ode_tab, "EDOs")

        self.init_derivative_ui()
        self.init_ode_ui()
        self.add_menu_bar()

    def init_derivative_ui(self):
        self.deriv_func_input = QLineEdit(self)
        self.deriv_func_input.setPlaceholderText("Ejemplo: cos(x^2*y^2)*2*y^2*x")
        self.derivative_layout.addWidget(QLabel("Función f(x, y, ...):"))
        self.derivative_layout.addWidget(self.deriv_func_input)

        # Crear un QHBoxLayout para "Variable(s) de derivación" y "Orden de la derivada"
        var_order_layout = QHBoxLayout()

        # Variable(s) de derivación
        var_layout = QVBoxLayout()
        var_layout.addWidget(QLabel("Variable(s) de derivación:"))
        self.var_input = QLineEdit(self)
        self.var_input.setText("x")
        self.var_input.setToolTip("Variable(s) de derivación, ej: x o x,y")
        var_layout.addWidget(self.var_input)
        var_order_layout.addLayout(var_layout)

        # Orden de la derivada
        order_layout = QVBoxLayout()
        order_layout.addWidget(QLabel("Orden de la derivada:"))
        self.order_input = QLineEdit(self)
        self.order_input.setText("1")
        order_layout.addWidget(self.order_input)
        var_order_layout.addLayout(order_layout)

        # Asegurar que cada campo ocupe la mitad del espacio
        var_order_layout.setStretch(0, 1)  # Variable(s) de derivación ocupa la mitad
        var_order_layout.setStretch(1, 1)  # Orden de la derivada ocupa la mitad

        # Añadir el layout horizontal al layout principal
        self.derivative_layout.addLayout(var_order_layout)

        self.deriv_type_combo = QComboBox(self)
        self.deriv_type_combo.addItems(["Indefinida", "Definida", "Parcial"])
        self.derivative_layout.addWidget(QLabel("Tipo de derivada:"))
        self.derivative_layout.addWidget(self.deriv_type_combo)

        self.limits_input = QLineEdit(self)
        self.limits_input.setPlaceholderText("Ejemplo: -2, 2 (solo para derivadas definidas)")
        self.limits_input.setEnabled(False)
        self.deriv_type_combo.currentTextChanged.connect(self.toggle_limits_input)
        self.derivative_layout.addWidget(QLabel("Límites (a, b):"))
        self.derivative_layout.addWidget(self.limits_input)

        self.deriv_button = QPushButton("Calcular Derivada", self)
        self.deriv_button.clicked.connect(self.calculate_derivative)
        self.derivative_layout.addWidget(self.deriv_button)

        self.deriv_result_text = QTextEdit(self)
        self.deriv_result_text.setReadOnly(True)
        self.deriv_result_text.setFixedHeight(100)
        self.derivative_layout.addWidget(QLabel("Resultado:"))
        self.derivative_layout.addWidget(self.deriv_result_text)

        self.copy_deriv_button = QPushButton("Copiar Resultado", self)
        self.copy_deriv_button.clicked.connect(self.copy_deriv_result)
        self.derivative_layout.addWidget(self.copy_deriv_button)

        self.deriv_figure = plt.figure()
        self.deriv_canvas = FigureCanvas(self.deriv_figure)
        self.right_layout.addWidget(self.deriv_canvas)

    def init_ode_ui(self):
        self.ode_input = QLineEdit(self)
        self.ode_input.setPlaceholderText("Ejemplo: y' = -2*y o 2*y' - y = 4*sin(3*t)")
        self.ode_layout.addWidget(QLabel("Ecuación diferencial:"))
        self.ode_layout.addWidget(self.ode_input)

        # Crear un QHBoxLayout para "Variable dependiente" y "Condición inicial"
        dep_cond_layout = QHBoxLayout()

        # Variable dependiente
        dep_layout = QVBoxLayout()
        dep_layout.addWidget(QLabel("Variable dependiente:"))
        self.dep_var_input = QLineEdit(self)
        self.dep_var_input.setText("y")  # Valor predeterminado
        self.dep_var_input.setPlaceholderText("Ejemplo: y, C")
        dep_layout.addWidget(self.dep_var_input)
        dep_cond_layout.addLayout(dep_layout)

        # Condición inicial
        cond_layout = QVBoxLayout()
        cond_layout.addWidget(QLabel("Condición inicial:"))
        self.initial_cond_input = QLineEdit(self)
        self.initial_cond_input.setPlaceholderText("Ejemplo: y(0) = 1")
        cond_layout.addWidget(self.initial_cond_input)
        dep_cond_layout.addLayout(cond_layout)

        # Asegurar que cada campo ocupe la mitad del espacio
        dep_cond_layout.setStretch(0, 1)  # Variable dependiente ocupa la mitad
        dep_cond_layout.setStretch(1, 1)  # Condición inicial ocupa la mitad

        # Añadir el layout horizontal al layout principal
        self.ode_layout.addLayout(dep_cond_layout)

        self.params_input = QLineEdit(self)
        self.params_input.setPlaceholderText("Ejemplo: k=0.1, M=10214")
        self.ode_layout.addWidget(QLabel("Parámetros (nombre=valor, separados por coma):"))
        self.ode_layout.addWidget(self.params_input)

        self.time_range_input = QLineEdit(self)
        self.time_range_input.setText("0, 10")
        self.ode_layout.addWidget(QLabel("Rango de tiempo (t0, tf):"))
        self.ode_layout.addWidget(self.time_range_input)

        self.ode_button = QPushButton("Resolver EDO", self)
        self.ode_button.clicked.connect(self.solve_ode)
        self.ode_layout.addWidget(self.ode_button)

        self.ode_result_text = QTextEdit(self)
        self.ode_result_text.setReadOnly(True)
        self.ode_result_text.setFixedHeight(100)
        self.ode_layout.addWidget(QLabel("Resultado:"))
        self.ode_layout.addWidget(self.ode_result_text)

        self.copy_ode_button = QPushButton("Copiar Resultado", self)
        self.copy_ode_button.clicked.connect(self.copy_ode_result)
        self.ode_layout.addWidget(self.copy_ode_button)

        self.ode_figure, self.ode_ax = plt.subplots()
        self.ode_canvas = FigureCanvas(self.ode_figure)
        self.right_layout.addWidget(self.ode_canvas)

    def add_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Opciones")
        clear_action = QAction("Limpiar Todo", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

    def toggle_limits_input(self, text):
        self.limits_input.setEnabled(text == "Definida")

    def preprocess_derivative(self, expr):
        """Preprocesa la entrada para derivadas."""
        expr = expr.strip()
        if not expr:
            raise ValueError("La entrada no puede estar vacía")
        expr = expr.replace('^', '**')
        expr = re.sub(r'\be\b(?!\w)', 'exp(1)', expr)
        expr = re.sub(r'e\^([-\w\d()*/+]+)', r'exp(\1)', expr)
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        sympy_funcs = ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']
        for func in sympy_funcs:
            expr = re.sub(rf'({func})\(', r'\1(', expr)  # Asegura que las funciones se interpreten correctamente
        return expr

    def preprocess_ode(self, expr, dep_var):
        """Preprocesa la entrada para EDOs."""
        expr = expr.strip()
        if not expr:
            raise ValueError("La entrada no puede estar vacía")
        expr = expr.replace('^', '**')
        expr = re.sub(r'\be\b(?!\w)', 'exp(1)', expr)
        expr = re.sub(r'e\^([-\w\d()*/+]+)', r'exp(\1)', expr)
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        # Reemplazar la derivada (por ejemplo, C' o y')
        expr = re.sub(rf'{dep_var}\'', f'Derivative({dep_var}(t), t)', expr)
        # Reemplazar la variable dependiente (por ejemplo, C o y)
        expr = re.sub(rf'\b{dep_var}\b(?!\()', f'{dep_var}(t)', expr)
        return expr

    def format_expression(self, expr):
        """Convierte una expresión simbólica a una cadena con formato a·x^b·y^c, con coeficientes al principio."""
        if isinstance(expr, sp.Number):
            # Convertir el número a float y redondear a 4 decimales
            num = float(expr)
            # Redondear a 4 decimales
            num_rounded = round(num, 4)
            # Convertir a cadena, eliminando ceros innecesarios
            if num_rounded.is_integer():
                return str(int(num_rounded))  # Si es un entero, eliminar los decimales
            else:
                return f"{num_rounded:.4f}".rstrip('0').rstrip('.')  # Mostrar hasta 4 decimales, eliminar ceros y punto innecesarios
        if isinstance(expr, sp.Symbol):
            return str(expr)
        if isinstance(expr, sp.Pow):
            base, exp = expr.args
            return f"{self.format_expression(base)}^{self.format_expression(exp)}"
        if isinstance(expr, sp.Mul):
            # Separar el coeficiente numérico (si existe) y el resto de los factores
            coeff = 1
            other_factors = []
            for factor in expr.args:
                if isinstance(factor, sp.Number):
                    coeff *= float(factor)  # Acumular el coeficiente numérico como float
                else:
                    other_factors.append(factor)
            
            # Ordenar los factores no numéricos (símbolos, potencias, funciones) alfabéticamente
            other_factors.sort(key=lambda x: str(x))
            
            # Formatear los factores no numéricos
            formatted_factors = [self.format_expression(factor) for factor in other_factors]
            
            # Redondear el coeficiente a 4 decimales
            coeff_rounded = round(coeff, 4)
            # Convertir el coeficiente a cadena, eliminando ceros innecesarios
            if coeff_rounded.is_integer():
                coeff_str = str(int(coeff_rounded))
            else:
                coeff_str = f"{coeff_rounded:.4f}".rstrip('0').rstrip('.')

            # Si el coeficiente es 1, no lo mostramos (excepto si no hay otros factores)
            if coeff_rounded == 1 and formatted_factors:
                return "·".join(formatted_factors)
            elif coeff_rounded == -1 and formatted_factors:
                return f"-{'·'.join(formatted_factors)}"
            else:
                # Incluir el coeficiente al principio
                formatted_factors.insert(0, coeff_str)
                return "·".join(formatted_factors)
        if isinstance(expr, sp.Add):
            return " + ".join(self.format_expression(term) for term in sorted(expr.args, key=lambda x: str(x)))
        if isinstance(expr, sp.Function):
            # Manejar funciones como exp, sin, cos, etc.
            return f"{expr.func.__name__}({self.format_expression(expr.args[0])})"
        return str(expr)
    
    def calculate_derivative(self):
        self.deriv_figure.clear()
        self.deriv_canvas.draw()
        try:
            func_str = self.preprocess_derivative(self.deriv_func_input.text())
            var_str = self.var_input.text().strip()
            order = int(self.order_input.text().strip())
            deriv_type = self.deriv_type_combo.currentText()
            limits = self.limits_input.text().strip() if deriv_type == "Definida" else None

            if not var_str:
                raise ValueError("Debe especificar al menos una variable")
            if order <= 0:
                raise ValueError("El orden debe ser un entero positivo")

            # Definir las variables de derivación
            vars_dict = {var.strip(): sp.Symbol(var.strip()) for var in var_str.split(",")}
            func = sp.sympify(func_str, locals=vars_dict)

            if deriv_type == "Indefinida" or deriv_type == "Parcial":
                derivative = func
                vars_list = [sp.Symbol(var) for var in var_str.split(",")]
                for var in vars_list:
                    for _ in range(order if len(vars_list) == 1 else 1):
                        derivative = sp.diff(derivative, var)
                # Formato del resultado al estilo de tu compañero con · para multiplicación
                var_deriv = vars_list[0]  # Tomar la primera variable de derivación
                func_formatted = self.format_expression(func)
                deriv_formatted = self.format_expression(derivative)
                result_text = f"∂f/∂{str(var_deriv)} de {func_formatted} es:\n{deriv_formatted}"
                self.deriv_result_text.setPlainText(result_text)

                # Identificar todas las variables presentes en la función
                all_vars = list(func.free_symbols)
                if not all_vars:
                    raise ValueError("La función no contiene variables simbólicas")

                # Determinar si graficar en 2D o 3D
                if len(all_vars) == 1:
                    # Caso de una sola variable (gráfico 2D)
                    x = all_vars[0]
                    x_vals = np.linspace(-10, 10, 400)
                    f_lambdified = sp.lambdify(x, func, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'exp': np.exp}])
                    df_lambdified = sp.lambdify(x, derivative, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'exp': np.exp}])
                    y_vals = f_lambdified(x_vals)
                    dy_vals = df_lambdified(x_vals)

                    # Verificar que los valores sean finitos
                    if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)) or np.any(np.isnan(dy_vals)) or np.any(np.isinf(dy_vals)):
                        raise ValueError("La función o su derivada genera valores indefinidos o infinitos")

                    ax = self.deriv_figure.add_subplot(111)
                    ax.plot(x_vals, y_vals, label=r'$f(x)$')
                    ax.plot(x_vals, dy_vals, label=f"$f^{{{order}}}(x)$", linestyle='dashed')
                    ax.legend()
                else:
                    # Caso de dos o más variables (gráfico 3D para derivada parcial)
                    if len(all_vars) < 2:
                        raise ValueError("Se necesitan al menos dos variables para graficar en 3D")
                    
                    x, y = all_vars[0], all_vars[1]  # Tomar las dos primeras variables
                    x_vals = np.linspace(0, 5, 50)  # Mitad derecha
                    y_vals = np.linspace(0, 5, 50)  # Mitad derecha
                    X, Y = np.meshgrid(x_vals, y_vals)

                    # Simplificar la derivada
                    derivative_simplified = sp.simplify(derivative)

                    # Sustituir las variables adicionales (si hay más de 2)
                    extra_vars = {var: 1 for var in all_vars if var not in [x, y]}
                    derivative_substituted = derivative_simplified.subs(extra_vars)

                    # Convertir la derivada a una función numérica
                    df_lambdified = sp.lambdify((x, y), derivative_substituted, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'exp': np.exp}])

                    # Evaluar la derivada en la malla
                    Z_deriv = df_lambdified(X, Y)

                    # Verificar que los valores sean finitos
                    if np.any(np.isnan(Z_deriv)) or np.any(np.isinf(Z_deriv)):
                        raise ValueError("La derivada parcial genera valores indefinidos o infinitos")

                    # Graficar en 3D
                    ax = self.deriv_figure.add_subplot(111, projection='3d')
                    surf = ax.plot_surface(X, Y, Z_deriv, cmap='viridis')
                    ax.set_xlabel(str(x))
                    ax.set_ylabel(str(y))
                    ax.set_zlabel(f'∂f/∂{str(var_deriv)}')
                    ax.set_xlim(0, 5)  # Mitad derecha
                    ax.set_ylim(0, 5)  # Mitad derecha
                    self.deriv_figure.colorbar(surf, ax=ax, shrink=0.5, aspect=5)  # Agregar barra de color

                self.deriv_canvas.draw()

            elif deriv_type == "Definida":
                if not limits or ',' not in limits:
                    raise ValueError("Debe especificar límites como 'a, b'")
                a, b = map(float, limits.split(','))
                var = sp.Symbol(var_str.split(",")[0])
                integral = sp.integrate(func, (var, a, b))
                result_text = f"Derivada definida de {a} a {b}: {self.format_expression(integral)}"
                self.deriv_result_text.setPlainText(result_text)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en el cálculo: {str(e)}")

    def solve_ode(self):
        self.ode_ax.clear()
        self.ode_canvas.draw()
        try:
            ode_str = self.ode_input.text()
            dep_var = self.dep_var_input.text().strip()  # Leer la variable dependiente
            initial_cond = self.initial_cond_input.text().strip()
            time_range = [float(t.strip()) for t in self.time_range_input.text().split(",")]
            params_str = self.params_input.text().strip()  # Leer los parámetros

            if not dep_var:
                raise ValueError("Debe especificar la variable dependiente")

            # Preprocesar la ecuación con la variable dependiente
            ode_str = self.preprocess_ode(ode_str, dep_var)

            t = sp.Symbol('t')
            # Definir la variable dependiente como una función de t
            y_func = sp.Function(dep_var)  # Crear la función simbólica (por ejemplo, C)
            y = y_func(t)  # Definir y como C(t)

            if '=' in ode_str:
                # Parsear la ecuación, asegurándonos de que SymPy reconozca y_func como la función
                left, right = [sp.sympify(side.strip(), locals={dep_var: y_func, 't': t, 'Derivative': sp.Derivative})
                            for side in ode_str.split('=')]
                ode = sp.Eq(left, right)
            else:
                raise ValueError("La ecuación debe contener '='")

            # Parsear los parámetros (por ejemplo, "k=0.005, M=10214")
            params = {}
            if params_str:
                for param in params_str.split(","):
                    name, value = param.split("=")
                    params[sp.Symbol(name.strip())] = float(value.strip())

            # Resolver la EDO
            sol_general = sp.dsolve(ode, y)

            # Sustituir los parámetros en la solución general
            sol_general = sol_general.subs(params)

            # Aplicar la condición inicial
            match = re.match(rf"{dep_var}\((.*?)\)\s*=\s*(.*)", initial_cond) if initial_cond else None
            t0, y0 = (float(match.group(1)), float(match.group(2))) if match else (0, 1)
            if not match and not initial_cond:
                QMessageBox.information(self, "Info", f"Usando {dep_var}(0) = 1 por defecto.")

            C = sp.Symbol('C1')
            sol_particular = sol_general.rhs.subs(t, t0) - y0
            constants = sp.solve(sol_particular, C)
            sol_particular = sol_general.rhs if not constants else sol_general.rhs.subs(C, constants[0])

            # Sustituir los parámetros en la solución particular
            sol_particular = sol_particular.subs(params)

            # Resolver numéricamente para graficar
            y_prime = sp.solve(ode, sp.Derivative(y, t))[0]
            y_prime = y_prime.subs(params)  # Sustituir parámetros en la derivada

            # Crear una variable simbólica auxiliar para C
            C_var = sp.Symbol('C_var')  # Variable auxiliar para representar C(t)
            # Sustituir C(t) por C_var en la expresión de la derivada
            y_prime_sub = y_prime.subs(y, C_var)
            # Convertir la derivada a una función numérica
            ode_func = sp.lambdify((t, C_var), y_prime_sub, 'numpy')
            # Resolver numéricamente usando solve_ivp
            sol_num = solve_ivp(lambda t, y: ode_func(t, y), time_range, [y0], t_eval=np.linspace(time_range[0], time_range[1], 100))

            # Formatear el resultado usando format_expression
            sol_general_formatted = self.format_expression(sol_general.rhs)
            sol_particular_formatted = self.format_expression(sol_particular)
            result_text = f"Solución General: {sol_general_formatted}\nSolución Particular: {sol_particular_formatted}"
            self.ode_result_text.setPlainText(result_text)

            # Graficar
            self.ode_ax.plot(sol_num.t, sol_num.y[0], label='Solución Numérica')
            self.ode_ax.scatter([t0], [y0], color='red', label='Condición Inicial')
            self.ode_ax.legend()
            self.ode_ax.set_xlabel('t (días)')
            self.ode_ax.set_ylabel(f'{dep_var}(t)')
            self.ode_canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al resolver la EDO: {str(e)}")

    def copy_deriv_result(self):
        QApplication.clipboard().setText(self.deriv_result_text.toPlainText())

    def copy_ode_result(self):
        QApplication.clipboard().setText(self.ode_result_text.toPlainText())

    def clear_all(self):
        self.deriv_func_input.clear()
        self.var_input.setText("x")
        self.order_input.setText("1")
        self.deriv_result_text.clear()
        self.deriv_figure.clear()
        self.deriv_canvas.draw()

        self.ode_input.clear()
        self.initial_cond_input.clear()
        self.time_range_input.setText("0, 10")
        self.ode_result_text.clear()
        self.ode_ax.clear()
        self.ode_canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DerivativeCalculator()
    window.show()
    sys.exit(app.exec())