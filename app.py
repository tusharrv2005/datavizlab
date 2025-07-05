from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# Create folders if not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file.filename == '':
        return "No file selected."

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath, encoding='latin1')
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error reading file: {e}"

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if len(numeric_cols) < 2:
        return "Not enough numeric columns to plot."

    df.to_csv('uploads/latest.csv', index=False)

    # Convert data to HTML table for preview
    preview_table = df.head(10).to_html(classes='table table-bordered table-striped', index=False)

    return render_template('select_columns.html', columns=numeric_cols, preview_table=preview_table)


    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath, encoding='latin1')
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error reading file: {e}"

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if len(numeric_cols) < 2:
        return "Not enough numeric columns to plot."

    df.to_csv('uploads/latest.csv', index=False)
    return render_template('select_columns.html', columns=numeric_cols)

@app.route('/plot', methods=['POST'])
def plot():
    x = request.form['x_column']
    y = request.form['y_column']
    chart_type = request.form['chart']
    title = request.form['title']

    df = pd.read_csv('uploads/latest.csv')

    plt.figure(figsize=(10, 5))
    
    try:
        if chart_type == 'bar':
            sns.barplot(data=df, x=x, y=y)
        elif chart_type == 'line':
            sns.lineplot(data=df, x=x, y=y)
        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x=x, y=y)
        elif chart_type == 'heatmap':
            numeric_df = df.apply(pd.to_numeric, errors='coerce')
            corr = numeric_df.corr()
            if corr.empty:
                return "No numeric data available for heatmap."
            sns.heatmap(corr, annot=True, cmap='coolwarm')
        else:
            return "Invalid chart type."

        plt.title(title)
        plt.xticks(rotation=45)
        plot_path = os.path.join(app.config['STATIC_FOLDER'], 'plot.png')
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        # Summary stats
        try:
            summary_table = df.describe().round(2).to_html(classes='table table-striped table-bordered', border=0)
        except Exception as e:
            summary_table = f"<p>Error generating summary statistics: {e}</p>"

        return render_template('result.html', plot_url='static/plot.png', stats_table=summary_table)

    except Exception as e:
        return f"Error generating plot: {e}"

@app.route('/download')
def download_plot():
    return send_file('static/plot.png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
