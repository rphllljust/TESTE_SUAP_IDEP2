from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command, CommandError
from django.db import connections


class Command(BaseCommand):
    help = (
        "Reseta o banco SQLite e recria as migrações/aplicações do projeto. "
        "Use para corrigir conflito com banco antigo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirma o reset sem prompt interativo.",
        )

    def handle(self, *args, **options):
        engine = settings.DATABASES["default"]["ENGINE"]
        if "sqlite3" not in engine:
            raise CommandError("Este comando suporta apenas SQLite.")

        confirmed = options["yes"]
        if not confirmed:
            answer = input("Isso vai apagar o banco atual. Continuar? [y/N]: ").strip().lower()
            if answer not in {"y", "yes", "s", "sim"}:
                self.stdout.write(self.style.WARNING("Operação cancelada."))
                return

        db_path = Path(settings.DATABASES["default"]["NAME"]).resolve()
        migrations_dir = Path(settings.BASE_DIR) / "core" / "migrations"

        for conn in connections.all():
            conn.close()

        if db_path.exists():
            db_path.unlink()
            self.stdout.write(self.style.WARNING(f"Banco removido: {db_path}"))
        else:
            self.stdout.write(self.style.WARNING("Banco SQLite não encontrado. Prosseguindo."))

        if migrations_dir.exists():
            for file in migrations_dir.glob("*.py"):
                if file.name != "__init__.py":
                    file.unlink()
            for file in migrations_dir.glob("*.pyc"):
                file.unlink()
            pycache = migrations_dir / "__pycache__"
            if pycache.exists():
                for file in pycache.glob("*"):
                    file.unlink()
                pycache.rmdir()

        self.stdout.write("Gerando novas migrações...")
        call_command("makemigrations", "core")

        self.stdout.write("Aplicando migrações...")
        call_command("migrate")

        self.stdout.write(self.style.SUCCESS("Banco recriado com sucesso."))
