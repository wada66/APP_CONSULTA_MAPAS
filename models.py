from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Tabela principal
class Mapa(db.Model):
    __tablename__ = 'mapa'
    id_mapa = db.Column(db.Integer, primary_key=True)
    n_chamada_mapa = db.Column(db.String(40))
    titulo_mapa = db.Column(db.String(500))
    escala_mapa = db.Column(db.String(40))
    articulacao_mapa = db.Column(db.String(40))
    projecao_mapa = db.Column(db.String(3))
    latitude_mapa = db.Column(db.String(40))
    longitude_mapa = db.Column(db.String(40))
    local_id = db.Column(db.Integer, db.ForeignKey('local.id_local'))
    data_mapa = db.Column(db.Date)
    colacao_mapa = db.Column(db.String(25))
    conteudo_mapa = db.Column(db.String(1000))
    nota_geral_mapa = db.Column(db.String(1000))
    aquisicao_mapa = db.Column(db.String(100))
    elaboracao_mapa = db.Column(db.String(300))
    assunto_mapa = db.Column(db.String(10000))
    fonte_mapa = db.Column(db.String(200))
    setor_mapa = db.Column(db.String(7))

    # Relacionamentos
    local = db.relationship('Local', backref='mapas', lazy=True)
    autores = db.relationship('Autor', secondary='mapa_autor', backref='mapas')
    executores = db.relationship('Executor', secondary='mapa_executor', backref='mapas')
    areas_geograficas = db.relationship('AreaGeografica', secondary='mapa_area_geografica', backref='mapas')


# Tabelas de apoio
class Local(db.Model):
    __tablename__ = 'local'
    id_local = db.Column(db.Integer, primary_key=True)
    nome_local = db.Column(db.String(40))


class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome_autor = db.Column(db.String(200))
    tipo_autor = db.Column(db.String(40))


class Executor(db.Model):
    __tablename__ = 'executor'
    id_executor = db.Column(db.Integer, primary_key=True)
    nome_executor = db.Column(db.String(200))


class AreaGeografica(db.Model):
    __tablename__ = 'area_geografica'
    id_area_geografica = db.Column(db.Integer, primary_key=True)
    nome_area_geografica = db.Column(db.String(40))


# Tabelas de junção
class MapaAutor(db.Model):
    __tablename__ = 'mapa_autor'
    id_mapa_autor = db.Column(db.Integer, primary_key=True)
    mapa_id = db.Column(db.Integer, db.ForeignKey('mapa.id_mapa'))
    autor_id = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


class MapaExecutor(db.Model):
    __tablename__ = 'mapa_executor'
    id_mapa_executor = db.Column(db.Integer, primary_key=True)
    mapa_id = db.Column(db.Integer, db.ForeignKey('mapa.id_mapa'))
    executor_id = db.Column(db.Integer, db.ForeignKey('executor.id_executor'))


class MapaAreaGeografica(db.Model):
    __tablename__ = 'mapa_area_geografica'
    id_mapa_area_geografica = db.Column(db.Integer, primary_key=True)
    mapa_id = db.Column(db.Integer, db.ForeignKey('mapa.id_mapa'))
    area_geografica_id = db.Column(db.Integer, db.ForeignKey('area_geografica.id_area_geografica'))