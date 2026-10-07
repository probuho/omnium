# Makefile para Omnium Suite

.PHONY: check lint fmt-check typecheck test mutaciones fmt clean install

# Verificación completa
check: lint typecheck test

# Linting con ruff
lint:
	ruff check src/ tests/

# Comprobacion de formato (informativa). El proyecto no usa ruff format:
# 28 de 32 archivos no siguen su estilo. NO forma parte de `make check`.
fmt-check:
	ruff format --check src/ tests/

# Formateo automático
fmt:
	ruff format src/ tests/

# Type checking con mypy
typecheck:
	mypy src/downloader_tui --strict

# Tests
test:
	pytest tests/ -v --tb=short

# Comprueba que los tests SIRVEN: reintroduce cada bug conocido y verifica que
# su test falla. Si algo pasa desapercibido, termina con error.
mutaciones:
	python scripts/comprobar_tests.py

# Instalación en modo desarrollo
install:
	pip install -e ".[dev]"

# Limpieza
clean:
	rm -rf __pycache__ src/downloader_tui/__pycache__ tests/__pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage dist build *.egg-info

# Verificación completa (igual que check)
all: check

# Ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  make check      - Verificación completa (lint + typecheck + test)"
	@echo "  make lint       - Linting con ruff"
	@echo "  make typecheck  - Type checking con mypy"
	@echo "  make test       - Ejecutar tests"
	@echo "  make mutaciones - Comprobar que los tests detectan los bugs conocidos"
	@echo "  make fmt        - Formateo automático con ruff"
	@echo "  make install    - Instalación en modo desarrollo"
	@echo "  make clean      - Limpieza de archivos temporales"
	@echo "  make help       - Mostrar esta ayuda"