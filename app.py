import re
from flask import Flask, render_template, request, jsonify
from config import Config
from models import db, Mapa, Local, Autor, Executor, AreaGeografica, MapaAutor, MapaExecutor
from datetime import datetime
from sqlalchemy import or_, extract

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.route('/')
def index():
    """Página inicial com estatísticas do acervo de mapas"""
    try:
        total_mapas = Mapa.query.count()
        total_autores = Autor.query.count()
    except Exception:
        total_mapas = 0
        total_autores = 0

    return render_template('index.html',
                           total_mapas=total_mapas,
                           total_autores=total_autores)


@app.route('/mapas', methods=['GET'])
def listar_mapas():
    """Lista mapas com filtros avançados"""
    
    # Carregar dados para os selects
    locais = Local.query.order_by(Local.nome_local).all()
    autores = Autor.query.order_by(Autor.nome_autor).all()
    executores = Executor.query.order_by(Executor.nome_executor).all()
    areas = AreaGeografica.query.order_by(AreaGeografica.nome_area_geografica).all()

    # Inicializar
    mapas = []
    filtros = {}

    # Verificar se há filtros na URL
    has_filters = any([
        request.args.get('id_mapa'),
        request.args.get('n_chamada_mapa'),
        request.args.get('titulo_mapa'),
        request.args.get('autor'),
        request.args.get('local_id'),
        request.args.get('mes'),
        request.args.get('ano'),
        request.args.get('conteudo_mapa'),
        request.args.get('executor'),
        request.args.get('area_id'),
        request.args.get('escala_mapa'),
        request.args.get('projecao_mapa'),
        request.args.get('setor_mapa')
    ])

    if has_filters or request.args.get('buscar'):
        query = Mapa.query

        # Filtro por ID
        if 'id_mapa' in request.args and request.args['id_mapa']:
            try:
                id_val = int(request.args['id_mapa'])
                query = query.filter(Mapa.id_mapa == id_val)
                filtros['id_mapa'] = request.args['id_mapa']
            except ValueError:
                pass

        # Filtro por Nº de Chamada
        if 'n_chamada_mapa' in request.args and request.args['n_chamada_mapa']:
            query = query.filter(Mapa.n_chamada_mapa.ilike(f"%{request.args['n_chamada_mapa']}%"))
            filtros['n_chamada_mapa'] = request.args['n_chamada_mapa']

        # Filtro por Título
        if 'titulo_mapa' in request.args and request.args['titulo_mapa']:
            termo = request.args['titulo_mapa'].strip()
            if termo:
                def criar_padrao_regex(palavra):
                    padrao = ''
                    for letra in palavra.lower():
                        if letra == 'a': padrao += '[aáàãâä]'
                        elif letra == 'e': padrao += '[eéèêë]'
                        elif letra == 'i': padrao += '[iíìîï]'
                        elif letra == 'o': padrao += '[oóòõôö]'
                        elif letra == 'u': padrao += '[uúùûü]'
                        elif letra == 'c': padrao += '[cç]'
                        else: padrao += re.escape(letra)
                    return padrao

                palavras = termo.split()
                condicoes = []
                for palavra in palavras:
                    if len(palavra) >= 2:
                        padrao = criar_padrao_regex(palavra)
                        try:
                            condicoes.append(Mapa.titulo_mapa.op('~*')(padrao))
                        except:
                            condicoes.append(Mapa.titulo_mapa.ilike(f"%{palavra}%"))
                if condicoes:
                    query = query.filter(*condicoes)
                filtros['titulo_mapa'] = termo

        # Filtro por Autor
        if 'autor' in request.args and request.args['autor']:
            termo = request.args['autor'].strip()
            if termo:
                def criar_padrao_regex(palavra):
                    padrao = ''
                    for letra in palavra.lower():
                        if letra == 'a': padrao += '[aáàãâä]'
                        elif letra == 'e': padrao += '[eéèêë]'
                        elif letra == 'i': padrao += '[iíìîï]'
                        elif letra == 'o': padrao += '[oóòõôö]'
                        elif letra == 'u': padrao += '[uúùûü]'
                        elif letra == 'c': padrao += '[cç]'
                        else: padrao += re.escape(letra)
                    return padrao

                palavras = termo.split()
                condicoes_autor = []

                for palavra in palavras:
                    if len(palavra) >= 2:
                        padrao = criar_padrao_regex(palavra)
                        try:
                            condicoes_autor.append(Autor.nome_autor.op('~*')(padrao))
                        except:
                            condicoes_autor.append(Autor.nome_autor.ilike(f"%{palavra}%"))
                    else:
                        condicoes_autor.append(Autor.nome_autor.ilike(f"%{palavra}%"))

                if condicoes_autor:
                    subquery = db.session.query(MapaAutor.mapa_id).join(
                        Autor, MapaAutor.autor_id == Autor.id_autor
                    ).filter(*condicoes_autor)
                    query = query.filter(Mapa.id_mapa.in_(subquery))

                filtros['autor'] = termo

        # Filtro por Local
        if 'local_id' in request.args and request.args['local_id']:
            try:
                query = query.filter(Mapa.local_id == int(request.args['local_id']))
                filtros['local_id'] = request.args['local_id']
            except ValueError:
                pass

        # Filtro por Data
        ano = request.args.get('ano', '')
        if ano.isdigit():
            ano_int = int(ano)
            query = query.filter(
                extract('year', Mapa.data_mapa) == ano_int
            )
            filtros['ano'] = ano
        

        # Filtro por Conteúdo
        if 'conteudo_mapa' in request.args and request.args['conteudo_mapa']:
            termo = request.args['conteudo_mapa'].strip()
            if termo:
                def criar_padrao_regex(palavra):
                    padrao = ''
                    for letra in palavra.lower():
                        if letra == 'a': padrao += '[aáàãâä]'
                        elif letra == 'e': padrao += '[eéèêë]'
                        elif letra == 'i': padrao += '[iíìîï]'
                        elif letra == 'o': padrao += '[oóòõôö]'
                        elif letra == 'u': padrao += '[uúùûü]'
                        elif letra == 'c': padrao += '[cç]'
                        else: padrao += re.escape(letra)
                    return padrao

                palavras = termo.split()
                condicoes = []

                for palavra in palavras:
                    if len(palavra) >= 2:
                        padrao = criar_padrao_regex(palavra)
                        try:
                            condicoes.append(Mapa.conteudo_mapa.op('~*')(padrao))
                        except:
                            condicoes.append(Mapa.conteudo_mapa.ilike(f"%{palavra}%"))
                    else:
                        condicoes.append(Mapa.conteudo_mapa.ilike(f"%{palavra}%"))

                if condicoes:
                    query = query.filter(*condicoes)
                filtros['conteudo_mapa'] = termo

        # Filtro por Executor
        if 'executor' in request.args and request.args['executor']:
            termo = request.args['executor'].strip()
            if termo:
                def criar_padrao_regex(palavra):
                    padrao = ''
                    for letra in palavra.lower():
                        if letra == 'a': padrao += '[aáàãâä]'
                        elif letra == 'e': padrao += '[eéèêë]'
                        elif letra == 'i': padrao += '[iíìîï]'
                        elif letra == 'o': padrao += '[oóòõôö]'
                        elif letra == 'u': padrao += '[uúùûü]'
                        elif letra == 'c': padrao += '[cç]'
                        else: padrao += re.escape(letra)
                    return padrao

                palavras = termo.split()
                condicoes_executor = []

                for palavra in palavras:
                    if len(palavra) >= 2:
                        padrao = criar_padrao_regex(palavra)
                        try:
                            condicoes_executor.append(Executor.nome_executor.op('~*')(padrao))
                        except:
                            condicoes_executor.append(Executor.nome_executor.ilike(f"%{palavra}%"))
                    else:
                        condicoes_executor.append(Executor.nome_executor.ilike(f"%{palavra}%"))

                if condicoes_executor:
                    subquery = db.session.query(MapaExecutor.mapa_id).join(
                        Executor, MapaExecutor.executor_id == Executor.id_executor
                    ).filter(*condicoes_executor)
                    query = query.filter(Mapa.id_mapa.in_(subquery))

                filtros['executor'] = termo

        # Filtro por Área Geográfica
        if 'area_id' in request.args and request.args['area_id']:
            try:
                area_id = int(request.args['area_id'])
                query = query.join(Mapa.areas_geograficas).filter(AreaGeografica.id_area_geografica == area_id)
                filtros['area_id'] = request.args['area_id']
            except ValueError:
                pass

        # Filtro por Escala
        if 'escala_mapa' in request.args and request.args['escala_mapa']:
            query = query.filter(Mapa.escala_mapa.ilike(f"%{request.args['escala_mapa']}%"))
            filtros['escala_mapa'] = request.args['escala_mapa']

        # Filtro por Projeção
        if 'projecao_mapa' in request.args and request.args['projecao_mapa']:
            query = query.filter(Mapa.projecao_mapa == request.args['projecao_mapa'])
            filtros['projecao_mapa'] = request.args['projecao_mapa']

        # Filtro por Setor
        if 'setor_mapa' in request.args and request.args['setor_mapa']:
            query = query.filter(Mapa.setor_mapa.ilike(f"%{request.args['setor_mapa']}%"))
            filtros['setor_mapa'] = request.args['setor_mapa']

        # Ordenar e executar
        mapas = query.order_by(Mapa.id_mapa.desc()).all()

    return render_template('mapas.html',
                           mapas=mapas,
                           locais=locais,
                           autores=autores,
                           executores=executores,
                           areas=areas,
                           filtros=filtros,
                           datetime=datetime,
                           has_filters=has_filters)


@app.route('/api/autores')
def get_autores():
    autores = Autor.query.order_by(Autor.nome_autor).all()
    return jsonify([{
        'id': a.id_autor,
        'nome': a.nome_autor,
        'tipo': a.tipo_autor
    } for a in autores])


@app.route('/api/executores')
def get_executores():
    executores = Executor.query.order_by(Executor.nome_executor).all()
    return jsonify([{
        'id': e.id_executor,
        'nome': e.nome_executor
    } for e in executores])


@app.route('/api/areas')
def get_areas():
    areas = AreaGeografica.query.order_by(AreaGeografica.nome_area_geografica).all()
    return jsonify([{
        'id': a.id_area_geografica,
        'nome': a.nome_area_geografica
    } for a in areas])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)