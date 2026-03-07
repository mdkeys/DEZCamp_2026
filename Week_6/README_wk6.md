**Use this to document notes and lessons learned throughout this module**

## Installing Java & PySpark
- I was in my DEZCamp_2026 folder when I followed the instructions from https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/06-batch/setup/macos.md. 
- After brew install, save the following environmental variables to .zshrc:
```
echo 'export JAVA_HOME=$(brew --prefix openjdk@17)' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
- `source` command reloads the file so changes take effect immediately. You can test by running `echo $JAVA_HOME` (result: /opt/homebrew/opt/openjdk@17) and `java --version` (openjdk 17.0.18 2026-01-20)

Output when running test_spark.py file:
```
WARNING: Using incubator modules: jdk.incubator.vector
Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
26/03/02 19:57:55 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Spark version: 4.1.1
+---+
| id|
+---+
|  0|
|  1|
|  2|
|  3|
|  4|
|  5|
|  6|
|  7|
|  8|
|  9|
+---+
```
Pyspark is installed inside the virtual environment that `uv` created and packages were installed into a .venv folder in my project directory (DEZCAMP_2026). To run commands through the uv virtual environment, prefix them with `uv run`:
- `uv run pyspark`
  - (when I run this, I get the SPARK version 4.1.1. I tried to test the scala code but it didn't work (invalid syntax))
- uv run jupyter notebook
  - first had to do `uv add jupyter`
  - After `uv run jupyter notebook` a browser with JN will appear. You can also copy and paste the url provided to access the notebook.