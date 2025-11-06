from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, String, INTEGER, Text, DATE, Numeric, text 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, scoped_session

app = Flask(__name__)
app.secret_key = "chave-secreta"

DB_URI = f"mysql+pymysql://root:20231101110020@localhost:3306/projeto_biblioteca"
engine = create_engine(DB_URI)
SessionLocal = scoped_session(sessionmaker(bind=engine))

class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    senha: Mapped[str] = mapped_column(String(100))

class Livros(Base):
    __tablename__ = "livros"
    ID_livro: Mapped[int] = mapped_column(INTEGER, primary_key = True, autoincrement = True)
    Titulo: Mapped[str] = mapped_column(String(255), nullable = False)
    Autor_id: Mapped[int] = mapped_column(INTEGER)
    ISBN: Mapped[str] = mapped_column(String(13), nullable = False)
    Ano_publicacao: Mapped[int] = mapped_column(INTEGER)
    Genero_id: Mapped[int] = mapped_column(INTEGER)
    Editora_id: Mapped[int] = mapped_column(INTEGER)
    Quantidade_disponivel: Mapped[int] = mapped_column(INTEGER)
    Resumo: Mapped[str] = mapped_column(Text)

Base.metadata.create_all(engine)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro_usuario", methods=["GET","POST"])
def cadastro_usuario():
    if request.method == 'POST':
        nome=request.form["nome"]
        email=request.form["email"]
        senha=request.form["senha"]
        
        with SessionLocal() as db:
            usuario_existente = db.query(Usuario).filter_by(email=email).first()

            if usuario_existente:
                return render_template("cadastro_usuario.html", erro="Email já cadastrado")

            db.add(Usuario(nome=nome, email=email, senha=senha))                    
            db.commit()
        return redirect(url_for('login'))
    return render_template("cadastro_usuario.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        senha = request.form["senha"]
        
        with SessionLocal() as db:
            usuario = db.query(Usuario).filter_by(email=email, senha=senha).first()
             
        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            return redirect(url_for('index'))
        else:
            return render_template("login.html", erro="Email ou senha incorretos")
    
    return render_template("login.html")

@app.route("/livros")
def livros():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    with SessionLocal() as db:
        sql_select = text("SELECT ID_livro, Titulo, Autor_id, ISBN, Ano_publicacao, Genero_id, Editora_id, Quantidade_disponivel, Resumo FROM livros")
        lista_livros = db.execute(sql_select).fetchall()
        return render_template("livros.html", produtos=lista_livros) 


@app.route("/criar_livro", methods=["GET", "POST"])
def criar_livro():
    if request.method == "POST":
        titulo = request.form["titulo"]
        autor_id = request.form["autor_id"]
        isbn = request.form["isbn"]
        ano_publicacao = request.form["ano_publicacao"] 
        genero_id = request.form["genero_id"]
        editora_id = request.form["editora_id"]
        quantidade_disponivel = request.form["quantidade_disponivel"]
        resumo = request.form["resumo"]
        
        with SessionLocal() as db:
            # Instanciando o objeto Livros com os atributos corretos
            livro = Livros(
                Titulo=titulo, 
                Autor_id=autor_id, 
                ISBN=isbn, 
                Ano_publicação=ano_publicacao, # Usando a grafia com 'ã' conforme o modelo [4]
                Genero_id=genero_id, 
                Editora_id=editora_id, 
                Quantidade_disponivel=quantidade_disponivel, 
                Resumo=resumo
            )
            
            db.add(livro) [6]
            db.commit() [6]
            return redirect(url_for("livros")) [6]
            
    return render_template("criar_livro.html") [6]

@app.route("/excluir_livro", methods=["GET", "POST"])
def excluir_livro():
    if request.method == "POST":
        titulo_a_excluir = request.form["titulo"] 
        
        with SessionLocal() as db:
            livro_a_excluir = db.query(Livros).filter_by(Titulo=titulo_a_excluir).first()
            
            if livro_a_excluir:
                db.delete(livro_a_excluir)
                db.commit()

    return render_template("excluir_livro.html") [8]

@app.route("/editar_livro/<int:ID_livro>", methods=["GET", "POST"])
def editar_livro(ID_livro):
    with SessionLocal() as db:
        livro = db.query(Livros).filter_by(ID_livro=ID_livro).first() 

        if not livro:
            return redirect(url_for('livros'))

        if request.method == "POST":
            livro.Titulo = request.form["titulo"]
            livro.Autor_id = request.form["autor_id"]
            livro.ISBN = request.form["isbn"]
            livro.Ano_publicação = request.form["ano_publicacao"]
            livro.Genero_id = request.form["genero_id"]
            livro.Editora_id = request.form["editora_id"]
            livro.Quantidade_disponivel = request.form["quantidade_disponivel"]
            livro.Resumo = request.form["resumo"]
            db.commit()
            return redirect(url_for("livros"))
        
        return render_template("editar_livros.html", livro=livro) 

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)