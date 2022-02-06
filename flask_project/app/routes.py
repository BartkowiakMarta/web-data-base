from flask import render_template, request, flash, url_for, redirect, Markup
from werkzeug.utils import secure_filename
from pathlib import Path
from app import app, db
from app.db_models import File, Stats
from app.statistics_models import statistic_models, plots_models
import pandas as pd
import os
import shutil

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title = "Flask Project - Home")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'GET':
            return render_template('upload.html', title="Flask Project - Upload")
        elif request.method == 'POST':
            f = request.files['file']
            df = pd.read_csv(f, sep="[,;|]")
            rows, cols = df.shape

            if rows > 1000 and cols > 20:
                flash(f'Ten plik jest za duży! Maksymalne wymiary to: 1000 rekordów, 20 kolumn.', 'danger')
                return redirect(url_for('upload'))
            else:
                filename = secure_filename(f.filename)
                folder_name = filename[:-4]
                path = r'app\static\files\{}'.format(folder_name)
                name_with_dir = os.path.join(path, filename)

                try:
                    open(name_with_dir, 'r')
                    flash(Markup('Ten plik już istnieje w bazie danych. Możesz go znaleźć w zakładce:\
                         <a href="/fileset">Lista plików.</a>'),'info')
                    return redirect(url_for('upload'))
                except:
                    os.makedirs(r'app\static\files\{}'.format(folder_name))
                    f.save(name_with_dir)
                    df.to_csv(name_with_dir, sep=';')
                    size = os.stat(name_with_dir).st_size
                    data = File(name = folder_name, rows = rows, columns = cols, size = size)
                    db.session.add(data)
                    db.session.commit()
                    statistic_models(folder_name, df, data)
                    plots_models(folder_name, df, data)          
        return redirect(url_for('fileset'))  
    except:
        flash('Nie udało się dodać pliku do bazy danych.', 'danger')
        return redirect(url_for('upload'))

@app.route('/fileset', methods=['GET'])
def fileset():
    try:
        files_to_list = db.session.query(File).order_by(File.name).all()
        return render_template('fileset.html', title="Flask Project - Fileset", files_to_list = files_to_list)
    except:
        flash(f'Nie udało się wyświetlić listy plików.', 'danger')
        return redirect(url_for('home'))

@app.route('/file_view/<int:file_id>',methods=['GET'])
def file_view(file_id):  
    try:
        file_to_open = File.query.get_or_404(file_id)
        numbers = db.session.query(Stats).filter((Stats.file_id == file_to_open.id)\
             & ((Stats.column_type == "int64") | (Stats.column_type == "float64"))).all()
        objects = db.session.query(Stats).filter((Stats.file_id == file_to_open.id)\
             & (Stats.column_type == "object")).all()
        datetimes = db.session.query(Stats).filter((Stats.file_id == file_to_open.id)\
             & (Stats.column_type == "datetime64")).all()
        return render_template('file_view.html', title="Flask Project - File View",\
             file_to_open = file_to_open, numbers = numbers, objects = objects,\
             datetimes = datetimes, file_id = file_id)
    except:
        flash(f'Nie ma takiego pliku w bazie danych.', 'danger')
        return redirect(url_for('fileset'))

@app.route('/plot_view/<int:file_id>/<path:plotname>', methods=['GET'])
def plot_view(file_id, plotname):
    try:
        source_file = File.query.get_or_404(file_id)
        return render_template('plot_view.html', source_file = source_file, plotname = plotname)
    except:
        flash('Nie udało się wyświetlić wykresu', 'danger')
        return render_template('home.html')
    
@app.route('/delete/<int:file_id>',methods = ['GET'])
def delete(file_id):
    try:
        file_to_delete = File.query.get_or_404(file_id)
        Stats.query.filter(Stats.file_id == file_to_delete.id).delete()
        File.query.filter(File.id == file_to_delete.id).delete()
        db.session.commit()
        path = os.path.join(r'app\static\files\{}'.format(file_to_delete.name))
        shutil.rmtree(path)
        
        flash(f'Plik został usunięty pomyślnie.', 'success')
        return redirect(url_for('fileset'))
    except:
        db.session.rollback()
        flash(f'Nie udało się usunąć pliku.', 'danger')
        return redirect(url_for('fileset'))