# Generated by Django 5.0.2 on 2024-03-08 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("domains", "0054_domainregistration_not_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="eurid_citizenship",
            field=models.CharField(
                blank=True,
                choices=[
                    ("AT", "Österreich (Austria)"),
                    ("BE", "België (Belgium)"),
                    ("BG", "България (Bulgaria)"),
                    ("CY", "Κύπρος (Cyprus)"),
                    ("CZ", "Česká republika (Czech Republic)"),
                    ("DE", "Deutschland (Germany)"),
                    ("DK", "Danmark (Denmark)"),
                    ("EE", "Eesti (Estonia)"),
                    ("ES", "España (Spain)"),
                    ("FI", "Suomi (Finland)"),
                    ("FR", "France"),
                    ("GR", "Ελλάδα (Greece)"),
                    ("HR", "Hrvatska (Croatia)"),
                    ("HU", "Magyarország (Hungary)"),
                    ("IE", "Éire (Ireland)"),
                    ("IT", "Italia (Italy)"),
                    ("LT", "Lietuva (Lithuania)"),
                    ("LU", "Lëtzebuerg (Luxembourg)"),
                    ("LV", "Latvija (Latvia)"),
                    ("MT", "Malta"),
                    ("NL", "Nederland (Netherlands)"),
                    ("PL", "Polska (Poland)"),
                    ("PT", "Portugal"),
                    ("RO", "România (Romania)"),
                    ("SE", "Sverige (Sweden)"),
                    ("SI", "Slovenija (Slovenia)"),
                    ("SK", "Slovensko (Slovakia)"),
                    ("IS", "Ísland (Iceland)"),
                    ("LI", "Liechtenstein"),
                    ("NO", "Norge (Norway)"),
                ],
                max_length=2,
                null=True,
            ),
        ),
    ]
