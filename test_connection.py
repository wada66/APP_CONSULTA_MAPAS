import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrado no .env")
    exit(1)

print(f"📊 Tentando conectar com: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

try:
    # Criar engine
    engine = create_engine(DATABASE_URL)
    
    # Testar conexão
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Conectado ao PostgreSQL!")
        print(f"   Versão: {version}")
        
        # Verificar se o banco existe
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"   Database atual: {db_name}")
        
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    print("\n🔧 Solução de problemas:")
    print("1. PostgreSQL está rodando?")
    print("2. Verifique usuário/senha no .env")
    print("3. Database 'MAPAS' existe?")
    print("4. Porta 5432 está acessível?")
    
    # Tentar criar database
    print("\n🛠️  Tentando criar database...")
    try:
        # Conectar ao PostgreSQL sem database específico
        base_url = DATABASE_URL.rsplit('/', 1)[0]  # Remove o nome do database
        temp_engine = create_engine(base_url + '/postgres')  # Conectar ao database padrão
        
        with temp_engine.connect() as conn:
            conn.execute(text("COMMIT"))
            conn.execute(text("CREATE DATABASE \"MAPAS\""))
            print("✅ Database 'MAPAS' criado com sucesso!")
    except Exception as create_error:
        print(f"❌ Não foi possível criar database: {create_error}")