from flask import Flask, render_template, request, session, redirect, url_for, flash, g
import os
import unidecode, materias, conteudos, avaliacoes, users


app = Flask(__name__)
uploaddir = 'static/imagens/userimgs/'
app.config['uploaddir'] = uploaddir
app.secret_key = "teste"


@app.before_request
def carregar_email():
    if 'usuario_email' in session:
        g.user = users.buscar_user(session['usuario_email'])


@app.route('/')
def home():
    return render_template('homepage.html', materias=materias.materias())


@app.route('/materia/<materialink>')
def materia(materialink):
    return render_template('materias.html',
                           materia=materialink,
                           conteudos=conteudos.contpormat(materialink))


@app.route('/nova_materia', methods=(['POST']))
def nova_materia():
    novamatnome = request.form['nomemat']
    novamatlink = unidecode.unidecode(novamatnome.replace(" ", "").lower())
    if materias.buscar_materia(novamatlink):
        flash("Matéria já existe.")
    else:
        materias.newmat(novamatlink, novamatnome)
    return redirect(url_for('home'))


@app.route('/materia/<materianome>/<conteudolink>')
def pagconteudo(materianome, conteudolink):
    conteudoatual = conteudos.buscar_cont(conteudolink)
    return render_template('conteudo.html',
                           materianome=materianome,
                           conteudopag=conteudoatual)


@app.route('/materia/<materianome>/criar_conteudo', methods=(['POST', 'GET']))
def addcont(materianome):
    if request.method == 'POST':
        cont = conteudos.add_cont(request, materianome, g.user)
        link = cont[0]
        cont[1].save(os.path.join(app.config['uploaddir'], cont[2]))
        return redirect(url_for('pagconteudo', materianome=materianome, conteudolink=link))
    
    if 'user' in g:
        return render_template('criarcont.html',
                               materia=materianome)
    
    return redirect(url_for('login'))


@app.route('/materia/<materianome>/<conteudolink>/avaliacoes', methods=(['POST', 'GET']))
def avaliacoespag(materianome, conteudolink):
    avaluser = None
    if 'user' in g:
        avaluser = avaliacoes.tem_aval(g.user.email, conteudolink)

    if request.method == 'POST':
        avaluser = avaliacoes.nova_aval(avaluser, g, request)

    conteudoatual = conteudos.buscar_cont(conteudolink)
    listatual = avaliacoes.listavalatual(conteudolink)
    avaliacoesatual, media = listatual[0], listatual[1]
    
    return render_template('avaliacoes.html', materianome=materianome,
                            conteudoatual=conteudoatual, avaliacoes=avaliacoesatual,
                            media=media, avaluser=avaluser)


@app.route('/cadastro', methods=(['POST', 'GET']))
def cadastropag():
    if request.method == 'POST':
        novo_user = users.novo_user(request)
        if novo_user[0]:
            flash(valido)
            return redirect(url_for('cadastropag'))
        session["usuario_email"] = novo_user[1]
        return redirect(url_for('home'))
    
    if 'user' in g:
        return redirect(url_for('perfil'))
    return render_template("cadastro.html")


@app.route('/login', methods=(['POST', 'GET']))
def login():
    if request.method == 'POST':
        login = users.login_user(request)
        if login:
            session["usuario_email"] = login
            return redirect(url_for('home'))
        flash("E-mail e/ou Senha inválidos.")
    
    if 'user' in g:
        return redirect(url_for('perfil'))
    return render_template('login.html')


@app.route('/logout', methods=(['POST']))
def logout():
    session.pop('usuario_email', None)
    return redirect(url_for('home'))


@app.route('/perfil')
def perfil():
    if 'user' in g:
        return render_template('perfil.html')
    return redirect(url_for('login'))


app.run(host='0.0.0.0', debug=True)
