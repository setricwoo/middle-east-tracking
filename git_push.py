import subprocess
import sys

# 仅推送 war-situation.html
try:
    result = subprocess.run(
        ['git', 'push', 'origin', 'main', '--force'],
        cwd='D:\\python_code\\海湾以来-最新',
        capture_output=True,
        text=True,
        timeout=120
    )
    print('STDOUT:', result.stdout)
    print('STDERR:', result.stderr)
    print('Return code:', result.returncode)
except Exception as e:
    print('Error:', e)
