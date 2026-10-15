using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

namespace AirportFwdDataAnalyzer
{
    public class LauncherForm : Form
    {
        private readonly Color navy = Color.FromArgb(11, 35, 64);
        private readonly Color blue = Color.FromArgb(20, 102, 204);
        private readonly Color teal = Color.FromArgb(0, 177, 190);
        private readonly Color amber = Color.FromArgb(255, 174, 24);
        private readonly string applicationRoot;

        public LauncherForm()
        {
            this.applicationRoot = AppDomain.CurrentDomain.BaseDirectory;

            this.Text = "Airport FWD Data Analyzer";
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(244, 248, 252);
            this.Font = new Font("Segoe UI", 10f, FontStyle.Regular, GraphicsUnit.Point);
            this.ClientSize = new Size(850, 530);
            this.MinimumSize = this.Size;
            this.MaximumSize = this.Size;

            try
            {
                this.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            }
            catch
            {
            }

            this.BuildInterface();
        }

        private void BuildInterface()
        {
            Panel headerPanel = new Panel();
            headerPanel.Dock = DockStyle.Top;
            headerPanel.Height = 205;
            headerPanel.BackColor = this.navy;

            PictureBox logoBox = new PictureBox();
            logoBox.Location = new Point(34, 22);
            logoBox.Size = new Size(160, 160);
            logoBox.SizeMode = PictureBoxSizeMode.Zoom;
            logoBox.BackColor = Color.Transparent;
            logoBox.Image = this.LoadLogo();
            headerPanel.Controls.Add(logoBox);

            Label titleLabel = new Label();
            titleLabel.Text = "AIRPORT FWD DATA ANALYZER";
            titleLabel.ForeColor = Color.White;
            titleLabel.Font = new Font("Segoe UI Semibold", 24f, FontStyle.Bold);
            titleLabel.AutoSize = true;
            titleLabel.Location = new Point(220, 46);
            headerPanel.Controls.Add(titleLabel);

            Label subtitleLabel = new Label();
            subtitleLabel.Text = "FWD/HWD backcalculation • pavement evaluation • FAA design";
            subtitleLabel.ForeColor = Color.FromArgb(194, 224, 242);
            subtitleLabel.Font = new Font("Segoe UI", 12f);
            subtitleLabel.AutoSize = true;
            subtitleLabel.Location = new Point(224, 103);
            headerPanel.Controls.Add(subtitleLabel);

            Label authorLabel = new Label();
            authorLabel.Text = "Developed and packaged by Sahil Yadav";
            authorLabel.ForeColor = Color.FromArgb(255, 205, 97);
            authorLabel.Font = new Font("Segoe UI Semibold", 10.5f);
            authorLabel.AutoSize = true;
            authorLabel.Location = new Point(224, 140);
            headerPanel.Controls.Add(authorLabel);

            this.Controls.Add(headerPanel);

            Label sectionLabel = new Label();
            sectionLabel.Text = "Choose an engineering tool";
            sectionLabel.ForeColor = this.navy;
            sectionLabel.Font = new Font("Segoe UI Semibold", 15f, FontStyle.Bold);
            sectionLabel.AutoSize = true;
            sectionLabel.Location = new Point(38, 228);
            this.Controls.Add(sectionLabel);

            Button backcalcBtn = this.CreateActionButton(
                "Open Backcalculation",
                "Import FWD/HWD data and backcalculate pavement layer properties",
                new Point(38, 270),
                this.blue);
            backcalcBtn.Click += (sender, e) => this.LaunchRelative("Airport_FWD_Backcalculation", "AirportFWD.Backcalculation.exe");
            this.Controls.Add(backcalcBtn);

            Button designBtn = this.CreateActionButton(
                "Open Pavement Design",
                "Design airport pavements and overlays with the supplied FAA engine",
                new Point(438, 270),
                this.teal);
            designBtn.Click += (sender, e) => this.LaunchRelative("Airport_FWD_Pavement_Design", "AirportFWD.PavementDesign.exe");
            this.Controls.Add(designBtn);

            Button manualsBtn = new Button();
            manualsBtn.Text = "Open manuals";
            manualsBtn.Location = new Point(38, 389);
            manualsBtn.Size = new Size(170, 39);
            manualsBtn.FlatStyle = FlatStyle.Flat;
            manualsBtn.BackColor = Color.White;
            manualsBtn.ForeColor = this.navy;
            manualsBtn.Cursor = Cursors.Hand;
            manualsBtn.FlatAppearance.BorderColor = Color.FromArgb(170, 190, 210);
            manualsBtn.Click += (sender, e) => this.OpenFolder("Manuals");
            this.Controls.Add(manualsBtn);

            LinkLabel repoLink = new LinkLabel();
            repoLink.Text = "github.com/sahilyadav-01/airport-fwd-data-analyzer";
            repoLink.LinkColor = this.blue;
            repoLink.ActiveLinkColor = this.teal;
            repoLink.AutoSize = true;
            repoLink.Location = new Point(230, 400);
            repoLink.LinkClicked += (sender, e) => this.StartShell("https://github.com/sahilyadav-01/airport-fwd-data-analyzer", this.applicationRoot);
            this.Controls.Add(repoLink);

            LinkLabel supportLink = new LinkLabel();
            supportLink.Text = "Support: skonetechsupport@gmail.com";
            supportLink.LinkColor = this.blue;
            supportLink.ActiveLinkColor = this.teal;
            supportLink.AutoSize = true;
            supportLink.Location = new Point(230, 424);
            supportLink.LinkClicked += (sender, e) => this.StartShell("mailto:skonetechsupport@gmail.com?subject=Airport%20FWD%20Data%20Analyzer%20Support", this.applicationRoot);
            this.Controls.Add(supportLink);

            Panel divider = new Panel();
            divider.Location = new Point(38, 455);
            divider.Size = new Size(774, 1);
            divider.BackColor = Color.FromArgb(210, 220, 230);
            this.Controls.Add(divider);

            Label copyrightLabel = new Label();
            copyrightLabel.Text = "Copyright © 2026 Sahil Yadav";
            copyrightLabel.ForeColor = this.navy;
            copyrightLabel.Font = new Font("Segoe UI Semibold", 9.5f);
            copyrightLabel.AutoSize = true;
            copyrightLabel.Location = new Point(38, 473);
            this.Controls.Add(copyrightLabel);

            Label disclaimerLabel = new Label();
            disclaimerLabel.Text = "Includes third-party FAA tools; original ownership and notices are retained.";
            disclaimerLabel.ForeColor = Color.FromArgb(90, 105, 120);
            disclaimerLabel.Font = new Font("Segoe UI", 8.5f);
            disclaimerLabel.AutoSize = true;
            disclaimerLabel.Location = new Point(382, 473);
            this.Controls.Add(disclaimerLabel);
        }

        private Button CreateActionButton(string title, string desc, Point location, Color borderColor)
        {
            Button btn = new Button();
            btn.Text = title + Environment.NewLine + desc;
            btn.TextAlign = ContentAlignment.MiddleLeft;
            btn.Padding = new Padding(18, 4, 12, 4);
            btn.Location = location;
            btn.Size = new Size(374, 96);
            btn.FlatStyle = FlatStyle.Flat;
            btn.BackColor = Color.White;
            btn.ForeColor = this.navy;
            btn.Cursor = Cursors.Hand;
            btn.Font = new Font("Segoe UI Semibold", 10.5f);
            btn.FlatAppearance.BorderColor = borderColor;
            btn.FlatAppearance.BorderSize = 3;
            btn.FlatAppearance.MouseOverBackColor = Color.FromArgb(235, 247, 252);
            return btn;
        }

        private Image LoadLogo()
        {
            using (Stream stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("AirportFwdDataAnalyzer.logo.png"))
            {
                if (stream == null) return null;
                using (Image img = Image.FromStream(stream))
                {
                    return new Bitmap(img);
                }
            }
        }

        private void LaunchRelative(string subfolder, string exeName)
        {
            string dir = Path.Combine(this.applicationRoot, subfolder);
            string exe = Path.Combine(dir, exeName);
            if (!File.Exists(exe))
            {
                MessageBox.Show("The required file was not found:\r\n" + exe + "\r\n\r\nKeep the complete package together.", "Airport FWD Data Analyzer", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                return;
            }
            try
            {
                this.StartShell(exe, dir);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Windows could not open the selected tool.\r\n\r\n" + ex.Message, "Airport FWD Data Analyzer", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
        }

        private void OpenFolder(string folderName)
        {
            string dir = Path.Combine(this.applicationRoot, folderName);
            if (!Directory.Exists(dir))
            {
                MessageBox.Show("Folder not found: " + dir, "Airport FWD Data Analyzer");
                return;
            }
            this.StartShell(dir, this.applicationRoot);
        }

        private void StartShell(string path, string workingDir)
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = path,
                WorkingDirectory = workingDir,
                UseShellExecute = true
            });
        }
    }
}
