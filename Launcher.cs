using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace VoiceStudioLauncher
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            try
            {
                string baseDir = AppDomain.CurrentDomain.BaseDirectory;
                string appDir = baseDir;

                if (!File.Exists(Path.Combine(appDir, "main.py")))
                {
                    string parent2 = Path.GetFullPath(Path.Combine(baseDir, @"..\.."));
                    if (File.Exists(Path.Combine(parent2, "main.py")))
                    {
                        appDir = parent2;
                    }
                    else if (File.Exists(@"E:\Projects_D\LocalTTS_App\main.py"))
                    {
                        appDir = @"E:\Projects_D\LocalTTS_App";
                    }
                }

                string mainPy = Path.Combine(appDir, "main.py");
                string pythonExe = @"C:\Users\goldl\AppData\Local\Programs\Python\Python312\pythonw.exe";
                if (!File.Exists(pythonExe))
                {
                    pythonExe = @"C:\Users\goldl\AppData\Local\Programs\Python\Python312\python.exe";
                }
                if (!File.Exists(pythonExe))
                {
                    pythonExe = "pythonw.exe";
                }

                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = pythonExe;
                psi.Arguments = "\"" + mainPy + "\"";
                if (args != null && args.Length > 0)
                {
                    foreach (string a in args)
                    {
                        psi.Arguments += " \"" + a.Replace("\"", "\\\"") + "\"";
                    }
                }
                psi.WorkingDirectory = appDir;
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                psi.EnvironmentVariables["PYTHONUTF8"] = "1";
                psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

                Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Failed to launch Voice Studio:\n" + ex.Message, "Voice Studio Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
