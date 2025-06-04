from flask import Flask, render_template, jsonify
import os
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'message': 'Serveur Flask opérationnel',
        'repository': os.environ.get('REPO_URL', 'Non configuré')
    })

@app.route('/api/repo-info')
def repo_info():
    try:
        # Obtenir les informations du repository Git
        repo_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], 
                                         cwd='/app', universal_newlines=True).strip()
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                            cwd='/app', universal_newlines=True).strip()
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                       cwd='/app', universal_newlines=True).strip()
        
        return jsonify({
            'repository_url': repo_url,
            'commit_hash': commit_hash[:8],
            'branch': branch,
            'last_commit': subprocess.check_output(['git', 'log', '-1', '--pretty=format:%s'], 
                                                 cwd='/app', universal_newlines=True).strip()
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'code': 200})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
