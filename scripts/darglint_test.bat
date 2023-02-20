@echo off
cd ..

echo "start darglint"

echo "pynecone folder"
for /R pynecone %%f in (*.py) do (
    echo %%f
    echo %%f|findstr /r "^.*pynecone\\pc\.py$"
    if errorlevel 1 (
        poetry run darglint %%f
    )
)

echo "tests folder"
for /R tests %%f in (*.py) do (
    echo %%f
    poetry run darglint %%f
)

echo "darglint finished"
pause
