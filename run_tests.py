#!/usr/bin/env python3
"""
Script para execução dos testes do sistema PetTransport.
"""
import argparse
import subprocess
import sys
import os


def run_command(command):
    """Executa um comando no terminal."""
    print(f"Executando: {' '.join(command)}")
    result = subprocess.run(command)
    return result.returncode


def main():
    """Função principal para execução dos testes."""
    parser = argparse.ArgumentParser(description="Executor de testes do PetTransport")
    parser.add_argument(
        "--mode",
        choices=["all", "user_creation", "coverage"],
        default="all",
        help="Modo de execução dos testes",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Exibir informações detalhadas"
    )
    args = parser.parse_args()

    verbose_flag = ["-v"] if args.verbose else []

    # Base do comando
    command = [sys.executable, "-m", "pytest"] + verbose_flag

    # Executar os testes conforme o modo selecionado
    if args.mode == "all":
        return run_command(command)
    elif args.mode == "user_creation":
        return run_command(command + ["tests/test_user_creation.py"])
    elif args.mode == "coverage":
        return run_command(
            command
            + [
                "--cov=app",
                "--cov=database_operations",
                "--cov=models",
                "--cov-report",
                "term-missing",
            ]
        )
    else:
        print(f"Modo desconhecido: {args.mode}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
