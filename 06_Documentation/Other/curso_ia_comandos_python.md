---
title: "Curso Ia Comandos Python"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Other/curso_ia_comandos_python.md"
---

# Guía de Referencia Rápida - Comandos Python para IA

## 🐍 Configuración del Entorno

### Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv ia_course_env

# Activar (Windows)
ia_course_env\Scripts\activate

# Activar (Linux/Mac)
source ia_course_env/bin/activate

# Desactivar
deactivate
```

### Instalar Librerías Esenciales
```bash
# Instalación básica
pip install numpy pandas matplotlib seaborn

# Machine Learning
pip install scikit-learn

# Deep Learning
pip install tensorflow keras

# Jupyter Notebook
pip install jupyter notebook

# Instalación completa
pip install -r requirements.txt
```

## 📊 Manipulación de Datos

### NumPy - Arrays y Operaciones
```python
import numpy as np

# Crear arrays
arr = np.array([1, 2, 3, 4, 5])
zeros = np.zeros((3, 4))
ones = np.ones((2, 3))
random = np.random.rand(3, 3)

# Operaciones básicas
arr.shape          # Forma del array
arr.dtype          # Tipo de datos
arr.reshape(5, 1)  # Cambiar forma
arr.mean()         # Media
arr.std()          # Desviación estándar
```

### Pandas - DataFrames
```python
import pandas as pd

# Crear DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': [9, 10, 11, 12]
})

# Operaciones básicas
df.head()          # Primeras 5 filas
df.info()          # Información del DataFrame
df.describe()      # Estadísticas descriptivas
df.isnull().sum()  # Valores nulos
df.dropna()        # Eliminar nulos
df.fillna(0)       # Rellenar nulos
```

## 🤖 Machine Learning

### Scikit-learn - Modelos Básicos
```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Entrenar modelo
model = LinearRegression()
model.fit(X_train, y_train)

# Predicciones
y_pred = model.predict(X_test)

# Evaluación
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
```

### Clasificación
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Modelo de clasificación
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predicciones
y_pred = clf.predict(X_test)

# Evaluación
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
```

## 🧠 Deep Learning

### TensorFlow/Keras - Red Neuronal Simple
```python
import tensorflow as tf
from tensorflow import keras

# Crear modelo
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(10, activation='softmax')
])

# Compilar modelo
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Entrenar
model.fit(X_train, y_train, epochs=10, validation_split=0.2)

# Evaluar
test_loss, test_acc = model.evaluate(X_test, y_test)
```

### CNN para Imágenes
```python
from tensorflow.keras import layers

# Modelo CNN
model = keras.Sequential([
    layers.Conv2D(32, 3, activation='relu', input_shape=(28, 28, 1)),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(10, activation='softmax')
])
```

## 📈 Visualización

### Matplotlib - Gráficos Básicos
```python
import matplotlib.pyplot as plt

# Gráfico de línea
plt.plot(x, y)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Título')
plt.show()

# Histograma
plt.hist(data, bins=30)
plt.show()

# Scatter plot
plt.scatter(x, y, alpha=0.5)
plt.show()
```

### Seaborn - Visualizaciones Avanzadas
```python
import seaborn as sns

# Heatmap
sns.heatmap(correlation_matrix, annot=True)

# Pairplot
sns.pairplot(df)

# Boxplot
sns.boxplot(x='category', y='value', data=df)

# Distplot
sns.distplot(data)
```

## 🔧 Utilidades Comunes

### Cargar y Guardar Datos
```python
# Cargar CSV
df = pd.read_csv('data.csv')

# Guardar CSV
df.to_csv('output.csv', index=False)

# Cargar Excel
df = pd.read_excel('data.xlsx')

# Guardar Excel
df.to_excel('output.xlsx', index=False)

# Cargar JSON
import json
with open('data.json', 'r') as f:
    data = json.load(f)
```

### Manejo de Archivos
```python
import os

# Crear directorio
os.makedirs('results', exist_ok=True)

# Listar archivos
files = os.listdir('data/')

# Verificar si existe
if os.path.exists('file.txt'):
    print("Archivo existe")

# Obtener tamaño
size = os.path.getsize('file.txt')
```

## 🎯 Comandos de Jupyter

### Comandos Mágicos
```python
# Información del sistema
%systeminfo

# Tiempo de ejecución
%%time
# código aquí

# Perfil de memoria
%memit
# código aquí

# Listar variables
%whos

# Historial de comandos
%history
```

### Navegación
```python
# Cambiar directorio
%cd /path/to/directory

# Listar archivos
%ls

# Ejecutar comando del sistema
!pip install package_name

# Ejecutar script
%run script.py
```

## 🚨 Solución de Problemas

### Errores Comunes
```python
# ImportError
try:
    import package_name
except ImportError:
    print("Instalar: pip install package_name")

# MemoryError
import gc
gc.collect()  # Liberar memoria

# ValueError
try:
    # código que puede fallar
    pass
except ValueError as e:
    print(f"Error: {e}")
```

### Debugging
```python
# Verificar tipos
print(type(variable))

# Verificar forma
print(array.shape)

# Verificar valores únicos
print(df['column'].unique())

# Verificar nulos
print(df.isnull().sum())
```

## 📚 Recursos Adicionales

### Documentación
- **NumPy**: https://numpy.org/doc/
- **Pandas**: https://pandas.pydata.org/docs/
- **Scikit-learn**: https://scikit-learn.org/stable/
- **TensorFlow**: https://www.tensorflow.org/api_docs

### Cheat Sheets
- **NumPy Cheat Sheet**: https://s3.amazonaws.com/assets.datacamp.com/blog_assets/Numpy_Python_Cheat_Sheet.pdf
- **Pandas Cheat Sheet**: https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf
- **Matplotlib Cheat Sheet**: https://matplotlib.org/cheatsheets/

### Comandos Útiles
```bash
# Verificar versión de Python
python --version

# Verificar paquetes instalados
pip list

# Actualizar pip
pip install --upgrade pip

# Instalar desde requirements
pip install -r requirements.txt

# Crear requirements.txt
pip freeze > requirements.txt
```

---
*Última actualización: Diciembre 2024*
