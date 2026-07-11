# Local Tooling

This project targets Java 21 for the Maven/Selenium/Cucumber side and Python 3.12.3 for the DeepEval CLI.

## Current Required Tools

- Eclipse Temurin JDK 21
- Apache Maven
- IntelliJ IDEA Community
- Python virtual environment in `.venv`

## Verification

```powershell
java -version
javac -version
mvn -version
.\.venv\Scripts\python.exe -m chatbot_eval metrics
.\.venv\Scripts\python.exe -m chatbot_eval evaluate examples\missing.json
```

Expected:

- `java` and `javac` should report major version `21`.
- `mvn -version` should report Java 21.
- `chatbot_eval metrics` should print JSON only.
- Missing evaluation input should return JSON with `status = ERROR` and exit code `2`.

## IntelliJ

Open `java-automation/` in IntelliJ IDEA Community as the Maven project and set:

- Project SDK: Eclipse Temurin 21
- Maven import: enabled
- Test runner: JUnit Platform

## Java 21 Path Note

If Java 23 is first on PATH, set `JAVA_HOME` to the JDK 21 directory and put `%JAVA_HOME%\bin` before Oracle Java entries in PATH.

## Maven Commands

Run Java smoke/unit tests only:

```powershell
.\java-automation\scripts\mvn-java21.ps1 test
```

Run browser-backed Cucumber scenarios after filling `java-automation/src/test/resources/config/chatbot.properties`:

```powershell
.\java-automation\scripts\mvn-java21.ps1 -Pcucumber verify
```

Portable Maven is installed under `.tools\apache-maven-3.9.16`; the helper script sets `JAVA_HOME` to Temurin 21 for the command it runs.
