from app import db
from app.db_models import Stats
from flask import flash, url_for, redirect
import numpy as np
import matplotlib.pyplot as plt


def statistic_models(folder_name, df, data):
    folder_name, df, data = folder_name, df, data
    try:
        for i in df:
            if df[i].dtype == "object":
                stats_objects = Stats(column_type = df[i].dtype.name,
                                       column_name=df[i].name,
                                       file_id = data.id, 
                                       unique_values_count = np.count_nonzero(df[i].unique()),
                                       null_values_count = int(df[i].isnull().sum()),
                                       nan_values_count = int(df[i].isna().sum()))
                db.session.add(stats_objects)

            elif df[i].dtype == "int64" or df[i].dtype == "float64":
                stats_numbers = Stats(column_type = df[i].dtype.name,
                                       file_id = data.id,
                                       column_name = df[i].name,
                                       min = round(df[i].min(), 2),
                                       max = round(df[i].max(), 2),
                                       avg = round(df[i].mean(), 2),
                                       me = round(df[i].median(), 2),
                                       std = round(df[i].std(), 2))
                db.session.add(stats_numbers)
                       
            elif df[i].dtype == "datetime64":
                stats_datetimes = Stats(column_type = df[i].dtype.name,
                                       column_name = df[i].name,
                                       file_id = data.id,
                                       first_date = df[i].min(),
                                       last_date = df[i].max())
                db.session.add(stats_datetimes)

            else:
                pass
        db.session.commit()
        flash(f"Plik '{folder_name}' został zapisany.", 'success')
        pass
    except:
        db.session.rollback()
        flash(f"Plik zawiera niepoprawne dane.", 'danger')
        return redirect(url_for('delete', file_id = data.id))

def plots_models(folder_name, df, data):
    folder_name, df, data = folder_name, df, data
    try:
        plots_to_be = db.session.query(Stats).filter((Stats.file_id == data.id)\
             & ((Stats.column_type == "int64") | (Stats.column_type == "float64")\
             | (Stats.column_type == "bool") | (Stats.column_type == "Category"))).all()
        names = []
        for plot_to_be in plots_to_be:
            names.append(plot_to_be.column_name)
        for name in names:
            df_2 = df.filter(regex=name)
            plt.hist(df_2)
            plt.title(name)
            plt.savefig(f"app/static/files/{folder_name}/{name}_hist.png")
            plt.show(block=False)
            plt.close()
        
        flash(f"Histogramy zostały wykonane.", 'success')
        return redirect(url_for('fileset'))
    except:
        flash(f"Histogramy nie zostały zapisane. ", 'danger')
        return redirect(url_for('fileset'))
    