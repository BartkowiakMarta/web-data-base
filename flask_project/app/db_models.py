from app import db

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('Nazwa', db.String(180), unique = True, nullable = True)   
    size = db.Column('Rozmiar', db.Integer, nullable = True)
    rows = db.Column('Wiersze', db.Integer, nullable = True)
    columns = db.Column('Kolumny', db.Integer, nullable = True)
    relations = db.relationship('Stats', backref='source_file', lazy='dynamic') 
    def __repr__(self):
        return f"- rozmiar: {round(self.size/1024, 2)} KB, {self.rows} rekordów, {self.columns} kolumn"

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    column_name = db.Column('Nazwa kolumny', db.String(30), nullable = True)
    column_type = db.Column('Typ kolumny', db.String(30), nullable = True)
    min = db.Column('Minimalna wartość', db.Float(),nullable=True)
    avg = db.Column('Średnia wartość', db.Float(),nullable=True)
    max = db.Column('Maksymalna wartość', db.Float(),nullable=True)
    me = db.Column('Mediana', db.Float(),nullable=True)
    std = db.Column('Odchylenie standardowe', db.Float(),nullable=True)
    first_date = db.Column('Pierwsza data', db.DateTime(),nullable=True)
    last_date = db.Column('Ostatnia data', db.DateTime(),nullable=True)
    unique_values_count = db.Column('Liczba unikalnych wartości', db.Integer(),nullable=True)
    null_values_count = db.Column('Liczba wartości pustych', db.Integer(),nullable=True)
    nan_values_count = db.Column('Liczba wartości typu NaN', db.Integer(),nullable=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)