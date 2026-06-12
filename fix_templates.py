import os, glob
base = 'app/templates/admin'
for fpath in glob.glob(os.path.join(base, '*.html')):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    new = content.replace("url_for('admin.", "url_for('manage.")
    if new != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new)
        print(f'Updated: {os.path.basename(fpath)}')
print('Done')
