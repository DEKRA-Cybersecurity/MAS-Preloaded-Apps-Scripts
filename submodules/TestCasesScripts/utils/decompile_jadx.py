import subprocess
import sys
import os

def print_progress(progress):
    # Calculate the progress bar width
    bar_width = 50
    progress_width = int(progress * bar_width / 100)
    
    # Build the progress bar string
    progress_bar = f"\r[{'=' * progress_width}{' ' * (bar_width - progress_width)}] {progress}%"
    
    # Clear the previous progress bar
    sys.stdout.write('\r' + ' ' * len(progress_bar) + '\r')
    
    # Print the updated progress bar
    sys.stdout.write(progress_bar)
    sys.stdout.flush()

def decompile(output_path, app_path, script_path):
    command = [script_path+"/tools/jadx/bin/jadx", "-d", output_path, app_path]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        progress = 0
        
        for line in process.stdout:
            if 'progress:' in line:
                # Extract the progress percentage from the line
                progress_line = line.split('(')[1].split('%')[0]
                progress = int(progress_line)
                
                # Update the progress bar
                print_progress(progress)
            elif 'INFO  - ' in line or 'ERROR -' in line:
                # Print non-progress lines
                if 'finished with errors' in line or 'INFO  - done' in line:
                    print_progress(100)
                    print('\r')

                print(line, end='')
                
        process.wait()

    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el comando:", e)

if __name__ == "__main__":

    output_path = os.path.join(sys.argv[1])
    app_path = os.path.join(sys.argv[2])
    script_path = os.path.join(sys.argv[3])

    decompile(output_path, app_path, script_path)

