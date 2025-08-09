# ==== CONFIGURAÇÕES ====
SVG_NAME ?= github_logo
SVG = svg/$(SVG_NAME).svg

INPUT_CSV = src/cpp/input.csv
OUTPUT_JSON = src/cpp/output.json

EXEC = src/cpp/bin/DFT

PARSER = src/python/parser.py
VISUAL = src/python/animar_fourier.py
# =======================

GREEN := \033[0;32m
YELLOW := \033[1;33m
RESET := \033[0m

# alvo padrão roda tudo com github_logo
all: build_and_run

# build padrão
build:
	@echo -e "$(YELLOW)Executando parser em Python...$(RESET)"
	python3 $(PARSER) --input $(SVG) --output $(INPUT_CSV)
	@echo -e "$(YELLOW)Compilando C++...$(RESET)"
	mkdir -p $(dir $(EXEC))
	g++ -std=c++23 -O3 -march=native src/cpp/DFT.cpp -o $(EXEC)
	@echo -e "$(YELLOW)Executando C++...$(RESET)"
	cd src && ./cpp/bin/DFT ../$(INPUT_CSV) ../$(OUTPUT_JSON)

build_and_run: build
	@echo -e "$(GREEN)Rodando visualização Python...$(RESET)"
	python3 $(VISUAL) --input $(OUTPUT_JSON)

run:
	@echo -e "$(GREEN)Rodando visualização Python...$(RESET)"
	python3 $(VISUAL) --input $(OUTPUT_JSON)

%:
	@echo -e "$(YELLOW)Construindo com SVG: $@$(RESET)"
	$(MAKE) build SVG_NAME=$@

run:
	@echo -e "$(GREEN)Rodando visualização Python...$(RESET)"
	python3 $(VISUAL) --input $(OUTPUT_JSON)

.PHONY: all build build_and_run run
