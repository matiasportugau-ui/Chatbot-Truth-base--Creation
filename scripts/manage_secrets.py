import keyring
import getpass
import sys
from pathlib import Path

# Add project root to sys.path to allow importing from config
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

try:
    from config.security_utils import KEYRING_SERVICE
except ImportError:
    KEYRING_SERVICE = "PanelinWolf"

def set_secret(service_name, key_name):
    print(f"\nConfigurando secreto para: {key_name}")
    value = getpass.getpass(f"Ingrese el valor para {key_name} (no se mostrará): ")
    if not value:
        print("Error: El valor no puede estar vacío.")
        return False
    
    try:
        keyring.set_password(service_name, key_name, value)
        print(f"✅ Secreto '{key_name}' guardado exitosamente en el Administrador de Credenciales.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar el secreto: {e}")
        return False

def main():
    SERVICE = KEYRING_SERVICE
    
    print("=" * 50)
    print("🔐 GESTOR DE SECRETOS PANELIN WOLF 🔐")
    print("=" * 50)
    print(f"Este script guardará sus API Keys en el Administrador de Credenciales de Windows.")
    print(f"Servicio: {SERVICE}")
    
    secrets = [
        "OPENAI_API_KEY", 
        "WOLF_API_KEY", 
        "OPENAI_ASSISTANT_ID",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "MONGODB_CONNECTION_STRING",
        "FACEBOOK_PAGE_ACCESS_TOKEN",
        "INSTAGRAM_ACCESS_TOKEN"
    ]
    
    print("\nSecretos disponibles para configurar:")
    for i, s in enumerate(secrets, 1):
        print(f"{i}. {s}")
    
    print("\nSeleccione los números (separados por coma) o 'all' para todos:")
    choice = input("> ").strip().lower()
    
    to_config = []
    if choice == 'all':
        to_config = secrets
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            to_config = [secrets[i] for i in indices if 0 <= i < len(secrets)]
        except:
            print("Selección inválida.")
            sys.exit(1)
            
    for secret in to_config:
        success = set_secret(SERVICE, secret)
        if not success:
            print(f"Fallo en {secret}, continuando...")
            
    print("\n" + "=" * 50)
    print("🎉 Proceso finalizado!")
    print("Asegúrese de que USE_KEYRING=true esté en su archivo .env")
    print("=" * 50)

if __name__ == "__main__":
    main()
