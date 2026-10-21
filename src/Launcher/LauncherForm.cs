using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

namespace AirportFwdDataAnalyzer
{
    public class LauncherForm : Form
    {
        private readonly Color navyDark = Color.FromArgb(10, 26, 46);
        private readonly Color navyLight = Color.FromArgb(20, 52, 90);
        private readonly Color accentCyan = Color.FromArgb(0, 180, 216);
        private readonly Color accentBlue = Color.FromArgb(20, 102, 204);
        private readonly Color accentTeal = Color.FromArgb(0, 150, 165);
        private readonly Color bgLight = Color.FromArgb(244, 247, 252);
        private readonly Color textDark = Color.FromArgb(18, 30, 49);
        private readonly Color textMuted = Color.FromArgb(85, 102, 122);
        private readonly Color borderLight = Color.FromArgb(218, 228, 238);

        private readonly string applicationRoot;
        private Image appLogo;

        private HeaderPanel headerPanel;
        private Panel contentPanel;
        private Panel footerPanel;
        private ModuleCard backcalcCard;
        private ModuleCard designCard;
        private Panel docsSectionPanel;
        private Label statusLabel;
        private Label copyLabel;

        public LauncherForm()
        {
            // Determine accurate application directory regardless of execution context
            string exePath = Assembly.GetExecutingAssembly().Location;
            if (!string.IsNullOrEmpty(exePath) && File.Exists(exePath))
            {
                this.applicationRoot = Path.GetDirectoryName(exePath);
            }
            else
            {
                this.applicationRoot = AppDomain.CurrentDomain.BaseDirectory;
            }

            this.SetStyle(ControlStyles.AllPaintingInWmPaint |
                          ControlStyles.UserPaint |
                          ControlStyles.DoubleBuffer |
                          ControlStyles.ResizeRedraw, true);

            this.Text = "Airport FWD Data Analyzer - Pavement Engineering Suite";
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = this.bgLight;
            this.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular, GraphicsUnit.Point);
            this.ClientSize = new Size(940, 640);
            this.MinimumSize = new Size(890, 600);
            this.MaximizeBox = true;
            this.AutoScaleMode = AutoScaleMode.Dpi;

            try
            {
                this.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            }
            catch
            {
            }

            this.appLogo = this.LoadLogo();

            this.BuildInterface();
            this.Resize += new EventHandler(this.OnFormResize);
        }

        private void BuildInterface()
        {
            this.SuspendLayout();

            // 1. Header Panel
            this.headerPanel = new HeaderPanel(this.navyDark, this.navyLight, this.accentCyan, this.appLogo);
            this.headerPanel.Dock = DockStyle.Top;
            this.headerPanel.Height = 175;
            this.Controls.Add(this.headerPanel);

            // 2. Footer Panel
            this.footerPanel = new Panel();
            this.footerPanel.Dock = DockStyle.Bottom;
            this.footerPanel.Height = 52;
            this.footerPanel.BackColor = Color.White;
            this.footerPanel.Paint += new PaintEventHandler(this.PaintFooter);
            this.BuildFooterContents();
            this.Controls.Add(this.footerPanel);

            // 3. Central Content Panel
            this.contentPanel = new Panel();
            this.contentPanel.Location = new Point(0, 175);
            this.contentPanel.Size = new Size(this.ClientSize.Width, this.ClientSize.Height - 175 - 52);
            this.contentPanel.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            this.contentPanel.BackColor = this.bgLight;
            this.contentPanel.Padding = new Padding(28, 14, 28, 10);
            this.Controls.Add(this.contentPanel);

            // Section Header Label
            Label sectionTitle = new Label();
            sectionTitle.Text = "ENGINEERING MODULES";
            sectionTitle.Font = new Font("Segoe UI", 11f, FontStyle.Bold);
            sectionTitle.ForeColor = this.navyDark;
            sectionTitle.Location = new Point(28, 12);
            sectionTitle.AutoSize = true;
            this.contentPanel.Controls.Add(sectionTitle);

            Label sectionSubtitle = new Label();
            sectionSubtitle.Text = "Select an operational workflow to launch the verified engineering engine";
            sectionSubtitle.Font = new Font("Segoe UI", 8.5f, FontStyle.Regular);
            sectionSubtitle.ForeColor = this.textMuted;
            sectionSubtitle.Location = new Point(29, 32);
            sectionSubtitle.AutoSize = true;
            this.contentPanel.Controls.Add(sectionSubtitle);

            // Module Card 1: Backcalculation
            string backcalcExe = Path.Combine(this.applicationRoot, "Airport_FWD_Backcalculation", "AirportFWD.Backcalculation.exe");
            bool backcalcFound = File.Exists(backcalcExe);
            this.backcalcCard = new ModuleCard(
                "Airport FWD Backcalculation",
                "Import FWD/HWD deflection basin data (Dynatest, KUAB, JILS, etc.), configure multi-layer pavement cross-sections, and backcalculate in-situ layer elastic moduli (E1, E2, ... En) using the FAA LEAF solver.",
                "BAKFAA v3.4.4 • LEAF Multilayer Solver",
                "Airport_FWD_Backcalculation",
                "AirportFWD.Backcalculation.exe",
                this.accentBlue,
                backcalcFound,
                ModuleCardType.Backcalculation
            );
            this.backcalcCard.CardClicked += new EventHandler(this.OnLaunchCard);
            this.contentPanel.Controls.Add(this.backcalcCard);

            // Module Card 2: Pavement Design
            string designExe = Path.Combine(this.applicationRoot, "Airport_FWD_Pavement_Design", "AirportFWD.PavementDesign.exe");
            bool designFound = File.Exists(designExe);
            this.designCard = new ModuleCard(
                "Airport FWD Pavement Design",
                "Compute runway and taxiway pavement thickness, structural overlays, and life cycle fatigue using Cumulative Damage Factor (CDF) analysis in strict compliance with FAA AC 150/5320-6G.",
                "FAARFIELD v2.1.2 • FAA AC 150/5320-6G Engine",
                "Airport_FWD_Pavement_Design",
                "AirportFWD.PavementDesign.exe",
                this.accentTeal,
                designFound,
                ModuleCardType.PavementDesign
            );
            this.designCard.CardClicked += new EventHandler(this.OnLaunchCard);
            this.contentPanel.Controls.Add(this.designCard);

            // Documentation & Utilities Section
            this.docsSectionPanel = new Panel();
            this.docsSectionPanel.BackColor = Color.White;
            this.docsSectionPanel.Paint += new PaintEventHandler(this.PaintDocsPanel);
            this.BuildDocsSection();
            this.contentPanel.Controls.Add(this.docsSectionPanel);

            this.ResumeLayout(true);
            this.LayoutCards();
        }

        private void BuildFooterContents()
        {
            this.statusLabel = new Label();
            this.statusLabel.UseMnemonic = false;
            bool allFound = File.Exists(Path.Combine(this.applicationRoot, "Airport_FWD_Backcalculation", "AirportFWD.Backcalculation.exe")) &&
                            File.Exists(Path.Combine(this.applicationRoot, "Airport_FWD_Pavement_Design", "AirportFWD.PavementDesign.exe"));
            this.statusLabel.Text = allFound ? "● System Status: Ready • Both Engineering Engines Verified (.NET 4.8)" : "⚠ Engine files missing • Please keep package files extracted together";
            this.statusLabel.ForeColor = allFound ? Color.FromArgb(20, 130, 60) : Color.FromArgb(200, 60, 40);
            this.statusLabel.Font = new Font("Segoe UI", 8.5f, FontStyle.Bold);
            this.statusLabel.AutoSize = true;
            this.statusLabel.Location = new Point(28, 17);
            this.footerPanel.Controls.Add(this.statusLabel);

            this.copyLabel = new Label();
            this.copyLabel.UseMnemonic = false;
            this.copyLabel.Text = "Copyright © 2026 Sahil Yadav • All Rights Reserved";
            this.copyLabel.Font = new Font("Segoe UI", 8.5f, FontStyle.Regular);
            this.copyLabel.ForeColor = this.textMuted;
            this.copyLabel.AutoSize = true;
            this.PositionCopyLabel();
            this.footerPanel.Controls.Add(this.copyLabel);
        }

        private void PositionCopyLabel()
        {
            if (this.copyLabel != null && this.footerPanel != null)
            {
                int x = this.footerPanel.ClientSize.Width - this.copyLabel.PreferredWidth - 28;
                if (x < 420) x = 420;
                this.copyLabel.Location = new Point(x, 17);
            }
        }

        private void BuildDocsSection()
        {
            Label docsTitle = new Label();
            docsTitle.UseMnemonic = false;
            docsTitle.Text = "RESOURCES & DOCUMENTATION";
            docsTitle.Font = new Font("Segoe UI", 8.5f, FontStyle.Bold);
            docsTitle.ForeColor = this.navyDark;
            docsTitle.Location = new Point(16, 10);
            docsTitle.AutoSize = true;
            this.docsSectionPanel.Controls.Add(docsTitle);

            // Manuals folder button
            Button openManualsBtn = this.CreatePillButton("Browse All Manuals", Color.FromArgb(240, 245, 252), this.navyDark, this.accentBlue);
            openManualsBtn.Location = new Point(16, 32);
            openManualsBtn.Size = new Size(135, 30);
            openManualsBtn.Click += (s, e) => this.OpenRelativeFolder("Manuals");
            this.docsSectionPanel.Controls.Add(openManualsBtn);

            // Backcalculation User Manual PDF
            Button backcalcPdfBtn = this.CreatePillButton("Backcalc Manual (PDF)", Color.FromArgb(245, 248, 252), this.textDark, Color.FromArgb(190, 205, 222));
            backcalcPdfBtn.Location = new Point(158, 32);
            backcalcPdfBtn.Size = new Size(150, 30);
            backcalcPdfBtn.Click += (s, e) => this.OpenRelativeFile("Manuals", "Airport FWD Data Analyzer - Backcalculation User Manual.pdf");
            this.docsSectionPanel.Controls.Add(backcalcPdfBtn);

            // Pavement Design Release Notes PDF
            Button designPdfBtn = this.CreatePillButton("Design Notes (PDF)", Color.FromArgb(245, 248, 252), this.textDark, Color.FromArgb(190, 205, 222));
            designPdfBtn.Location = new Point(315, 32);
            designPdfBtn.Size = new Size(135, 30);
            designPdfBtn.Click += (s, e) => this.OpenRelativeFile("Manuals", "Airport FWD Data Analyzer - Pavement Design Release Notes.pdf");
            this.docsSectionPanel.Controls.Add(designPdfBtn);

            // Presentation PDF
            Button presPdfBtn = this.CreatePillButton("Presentation (PDF)", Color.FromArgb(245, 248, 252), this.textDark, Color.FromArgb(190, 205, 222));
            presPdfBtn.Location = new Point(457, 32);
            presPdfBtn.Size = new Size(130, 30);
            presPdfBtn.Click += (s, e) => this.OpenRelativeFile("Manuals", "Airport FWD Data Analyzer - Backcalculation Presentation.pdf");
            this.docsSectionPanel.Controls.Add(presPdfBtn);

            // GitHub link
            LinkLabel repoLink = new LinkLabel();
            repoLink.Text = "GitHub Repository";
            repoLink.Font = new Font("Segoe UI", 8.5f, FontStyle.Regular);
            repoLink.LinkColor = this.accentBlue;
            repoLink.ActiveLinkColor = this.accentTeal;
            repoLink.AutoSize = true;
            repoLink.Location = new Point(602, 38);
            repoLink.LinkClicked += (s, e) => this.StartShell("https://github.com/sahilyadav-01/airport-fwd-data-analyzer", this.applicationRoot);
            this.docsSectionPanel.Controls.Add(repoLink);

            // Support link
            LinkLabel supportLink = new LinkLabel();
            supportLink.Text = "Technical Support :- skonetechsupport@gmail.com";
            supportLink.Font = new Font("Segoe UI", 8.5f, FontStyle.Regular);
            supportLink.LinkColor = this.accentBlue;
            supportLink.ActiveLinkColor = this.accentTeal;
            supportLink.AutoSize = true;
            supportLink.Location = new Point(720, 38);
            supportLink.LinkClicked += (s, e) => this.StartShell("mailto:skonetechsupport@gmail.com?subject=Airport%20FWD%20Data%20Analyzer%20Support", this.applicationRoot);
            this.docsSectionPanel.Controls.Add(supportLink);
        }

        private Button CreatePillButton(string text, Color backColor, Color textColor, Color borderColor)
        {
            Button btn = new Button();
            btn.Text = text;
            btn.FlatStyle = FlatStyle.Flat;
            btn.BackColor = backColor;
            btn.ForeColor = textColor;
            btn.Font = new Font("Segoe UI", 8f, FontStyle.Bold);
            btn.Cursor = Cursors.Hand;
            btn.FlatAppearance.BorderColor = borderColor;
            btn.FlatAppearance.BorderSize = 1;
            btn.FlatAppearance.MouseOverBackColor = Color.FromArgb(230, 240, 250);
            return btn;
        }

        private void LayoutCards()
        {
            if (this.contentPanel == null || this.backcalcCard == null || this.designCard == null)
                return;

            int padLeft = 28;
            int padTop = 56;
            int gap = 20;
            int availWidth = this.contentPanel.ClientSize.Width - (padLeft * 2);
            int cardWidth = (availWidth - gap) / 2;
            if (cardWidth < 380) cardWidth = 380;
            int cardHeight = 210;

            this.backcalcCard.Location = new Point(padLeft, padTop);
            this.backcalcCard.Size = new Size(cardWidth, cardHeight);

            this.designCard.Location = new Point(padLeft + cardWidth + gap, padTop);
            this.designCard.Size = new Size(cardWidth, cardHeight);

            int docsTop = padTop + cardHeight + 16;
            int docsWidth = (cardWidth * 2) + gap;
            this.docsSectionPanel.Location = new Point(padLeft, docsTop);
            this.docsSectionPanel.Size = new Size(docsWidth, 74);

            this.PositionCopyLabel();
        }

        private void OnFormResize(object sender, EventArgs e)
        {
            this.LayoutCards();
        }

        private void PaintFooter(object sender, PaintEventArgs e)
        {
            using (Pen borderPen = new Pen(this.borderLight, 1))
            {
                e.Graphics.DrawLine(borderPen, 0, 0, this.footerPanel.Width, 0);
            }
        }

        private void PaintDocsPanel(object sender, PaintEventArgs e)
        {
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            Rectangle rect = new Rectangle(0, 0, this.docsSectionPanel.Width - 1, this.docsSectionPanel.Height - 1);
            using (GraphicsPath path = GetRoundedRect(rect, 8))
            {
                using (Pen borderPen = new Pen(this.borderLight, 1))
                {
                    e.Graphics.DrawPath(borderPen, path);
                }
            }
        }

        public static GraphicsPath GetRoundedRect(Rectangle bounds, int radius)
        {
            int diameter = radius * 2;
            Size size = new Size(diameter, diameter);
            Rectangle arc = new Rectangle(bounds.Location, size);
            GraphicsPath path = new GraphicsPath();

            if (radius == 0)
            {
                path.AddRectangle(bounds);
                return path;
            }

            path.AddArc(arc, 180, 90);
            arc.X = bounds.Right - diameter;
            path.AddArc(arc, 270, 90);
            arc.Y = bounds.Bottom - diameter;
            path.AddArc(arc, 0, 90);
            arc.X = bounds.Left;
            path.AddArc(arc, 90, 90);
            path.CloseFigure();
            return path;
        }

        private void OnLaunchCard(object sender, EventArgs e)
        {
            ModuleCard card = sender as ModuleCard;
            if (card == null) return;
            this.LaunchRelative(card.Subfolder, card.ExecutableName);
        }

        private void LaunchRelative(string subfolder, string exeName)
        {
            string dir = Path.Combine(this.applicationRoot, subfolder);
            string exe = Path.Combine(dir, exeName);
            if (!File.Exists(exe))
            {
                MessageBox.Show(
                    "The required engineering application was not found:\r\n\r\n" + exe + "\r\n\r\nPlease ensure all package components remain extracted together.",
                    "Airport FWD Data Analyzer",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Exclamation
                );
                return;
            }
            try
            {
                this.StartShell(exe, dir);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Windows could not launch the selected application:\r\n\r\n" + ex.Message,
                    "Airport FWD Data Analyzer",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        private void OpenRelativeFolder(string folderName)
        {
            string dir = Path.Combine(this.applicationRoot, folderName);
            if (!Directory.Exists(dir))
            {
                MessageBox.Show("Folder not found:\r\n" + dir, "Airport FWD Data Analyzer");
                return;
            }
            this.StartShell(dir, this.applicationRoot);
        }

        private void OpenRelativeFile(string subfolder, string fileName)
        {
            string path = Path.Combine(this.applicationRoot, subfolder, fileName);
            if (!File.Exists(path))
            {
                MessageBox.Show("Document not found:\r\n" + path, "Airport FWD Data Analyzer");
                return;
            }
            this.StartShell(path, this.applicationRoot);
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

        private Image LoadLogo()
        {
            try
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
            catch
            {
                return null;
            }
        }
    }

    public enum ModuleCardType
    {
        Backcalculation,
        PavementDesign
    }

    public class ModuleCard : Control
    {
        public string Title { get; private set; }
        public string Description { get; private set; }
        public string EngineTag { get; private set; }
        public string Subfolder { get; private set; }
        public string ExecutableName { get; private set; }
        public Color AccentColor { get; private set; }
        public bool IsInstalled { get; private set; }
        public ModuleCardType CardType { get; private set; }

        public event EventHandler CardClicked;

        private bool isHovered = false;
        private bool isPressed = false;
        private Rectangle launchButtonRect;

        public ModuleCard(string title, string description, string engineTag, string subfolder, string exeName, Color accentColor, bool isInstalled, ModuleCardType cardType)
        {
            this.Title = title;
            this.Description = description;
            this.EngineTag = engineTag;
            this.Subfolder = subfolder;
            this.ExecutableName = exeName;
            this.AccentColor = accentColor;
            this.IsInstalled = isInstalled;
            this.CardType = cardType;

            this.SetStyle(ControlStyles.AllPaintingInWmPaint |
                          ControlStyles.UserPaint |
                          ControlStyles.DoubleBuffer |
                          ControlStyles.ResizeRedraw, true);

            this.Cursor = Cursors.Hand;
        }

        protected override void OnMouseEnter(EventArgs e)
        {
            base.OnMouseEnter(e);
            this.isHovered = true;
            this.Invalidate();
        }

        protected override void OnMouseLeave(EventArgs e)
        {
            base.OnMouseLeave(e);
            this.isHovered = false;
            this.isPressed = false;
            this.Invalidate();
        }

        protected override void OnMouseDown(MouseEventArgs e)
        {
            base.OnMouseDown(e);
            if (e.Button == MouseButtons.Left)
            {
                this.isPressed = true;
                this.Invalidate();
            }
        }

        protected override void OnMouseUp(MouseEventArgs e)
        {
            base.OnMouseUp(e);
            if (this.isPressed)
            {
                this.isPressed = false;
                this.Invalidate();
                if (this.ClientRectangle.Contains(e.Location))
                {
                    if (this.CardClicked != null)
                    {
                        this.CardClicked(this, EventArgs.Empty);
                    }
                }
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = TextRenderingHint.ClearTypeGridFit;

            Rectangle rect = new Rectangle(0, 0, this.Width - 1, this.Height - 1);
            int radius = 10;

            // Background color
            Color cardBg = Color.White;
            if (this.isPressed)
                cardBg = Color.FromArgb(235, 242, 250);
            else if (this.isHovered)
                cardBg = Color.FromArgb(248, 251, 255);

            using (GraphicsPath path = LauncherForm.GetRoundedRect(rect, radius))
            {
                using (SolidBrush bgBrush = new SolidBrush(cardBg))
                {
                    g.FillPath(bgBrush, path);
                }

                // Border
                Color borderColor = this.isHovered ? this.AccentColor : Color.FromArgb(215, 225, 235);
                float borderWidth = this.isHovered ? 2f : 1.2f;
                using (Pen borderPen = new Pen(borderColor, borderWidth))
                {
                    g.DrawPath(borderPen, path);
                }
            }

            // Top-left accent badge / icon box
            int iconBoxSize = 34;
            Rectangle iconRect = new Rectangle(18, 16, iconBoxSize, iconBoxSize);
            using (GraphicsPath iconPath = LauncherForm.GetRoundedRect(iconRect, 6))
            {
                using (SolidBrush iconBgBrush = new SolidBrush(Color.FromArgb(235, 242, 252)))
                {
                    g.FillPath(iconBgBrush, iconPath);
                }
                using (Pen iconBorder = new Pen(Color.FromArgb(195, 215, 240), 1f))
                {
                    g.DrawPath(iconBorder, iconPath);
                }
            }

            // Draw Icon graphic
            using (Pen pen = new Pen(this.AccentColor, 2f))
            {
                if (this.CardType == ModuleCardType.Backcalculation)
                {
                    // Deflection basin curve
                    g.DrawCurve(pen, new Point[] {
                        new Point(23, 24),
                        new Point(29, 36),
                        new Point(35, 42),
                        new Point(41, 36),
                        new Point(47, 24)
                    });
                }
                else
                {
                    // Pavement layers
                    g.DrawLine(pen, 24, 25, 46, 25);
                    g.DrawLine(pen, 24, 32, 46, 32);
                    g.DrawLine(pen, 24, 40, 46, 40);
                }
            }

            // Status Badge (Top-Right)
            string statusText = this.IsInstalled ? "● READY" : "⚠ NOT FOUND";
            Color statusTextColor = this.IsInstalled ? Color.FromArgb(20, 130, 60) : Color.FromArgb(200, 60, 40);
            Color statusBgColor = this.IsInstalled ? Color.FromArgb(232, 246, 235) : Color.FromArgb(254, 236, 236);

            using (Font statusFont = new Font("Segoe UI", 7.5f, FontStyle.Bold))
            {
                Size statusSize = TextRenderer.MeasureText(statusText, statusFont);
                Rectangle statusRect = new Rectangle(this.Width - statusSize.Width - 26, 16, statusSize.Width + 12, 22);
                using (GraphicsPath statusPath = LauncherForm.GetRoundedRect(statusRect, 5))
                {
                    using (SolidBrush sBrush = new SolidBrush(statusBgColor))
                    {
                        g.FillPath(sBrush, statusPath);
                    }
                }
                TextRenderer.DrawText(g, statusText, statusFont, new Point(statusRect.X + 6, statusRect.Y + 4), statusTextColor);
            }

            // Title
            using (Font titleFont = new Font("Segoe UI", 11.5f, FontStyle.Bold))
            {
                int titleAvailableWidth = this.Width - 62 - (this.Width - (this.Width - 95));
                Rectangle titleRect = new Rectangle(60, 18, this.Width - 165, 26);
                TextRenderer.DrawText(g, this.Title, titleFont, titleRect, Color.FromArgb(10, 26, 46),
                    TextFormatFlags.Left | TextFormatFlags.Top | TextFormatFlags.EndEllipsis);
            }

            // Description
            using (Font descFont = new Font("Segoe UI", 8.8f, FontStyle.Regular))
            {
                Rectangle descRect = new Rectangle(18, 60, this.Width - 36, 85);
                TextRenderer.DrawText(g, this.Description, descFont, descRect, Color.FromArgb(70, 85, 105),
                    TextFormatFlags.Left | TextFormatFlags.Top | TextFormatFlags.WordBreak);
            }

            // Bottom Divider line
            using (Pen divPen = new Pen(Color.FromArgb(238, 243, 248), 1f))
            {
                g.DrawLine(divPen, 18, this.Height - 48, this.Width - 18, this.Height - 48);
            }

            // Engine Tag (Bottom-Left)
            using (Font tagFont = new Font("Segoe UI", 8f, FontStyle.Regular))
            {
                Rectangle tagRect = new Rectangle(18, this.Height - 38, this.Width - 170, 24);
                TextRenderer.DrawText(g, this.EngineTag, tagFont, tagRect, Color.FromArgb(110, 125, 145),
                    TextFormatFlags.Left | TextFormatFlags.VerticalCenter | TextFormatFlags.EndEllipsis);
            }

            // Launch Button (Bottom-Right)
            int btnW = 126;
            int btnH = 30;
            this.launchButtonRect = new Rectangle(this.Width - btnW - 18, this.Height - 40, btnW, btnH);
            Color btnBg = this.isHovered ? this.AccentColor : Color.FromArgb(240, 245, 252);
            Color btnFg = this.isHovered ? Color.White : this.AccentColor;

            using (GraphicsPath btnPath = LauncherForm.GetRoundedRect(this.launchButtonRect, 5))
            {
                using (SolidBrush btnBrush = new SolidBrush(btnBg))
                {
                    g.FillPath(btnBrush, btnPath);
                }
                using (Pen btnPen = new Pen(this.AccentColor, 1f))
                {
                    g.DrawPath(btnPen, btnPath);
                }
            }

            using (Font btnFont = new Font("Segoe UI", 8.5f, FontStyle.Bold))
            {
                string btnText = "Launch Module  ➔";
                TextRenderer.DrawText(g, btnText, btnFont, this.launchButtonRect, btnFg,
                    TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter);
            }
        }
    }

    public class HeaderPanel : Panel
    {
        private Color darkColor;
        private Color lightColor;
        private Color accentLineColor;
        private Image logo;

        public HeaderPanel(Color darkColor, Color lightColor, Color accentLineColor, Image logo)
        {
            this.darkColor = darkColor;
            this.lightColor = lightColor;
            this.accentLineColor = accentLineColor;
            this.logo = logo;

            this.SetStyle(ControlStyles.AllPaintingInWmPaint |
                          ControlStyles.UserPaint |
                          ControlStyles.DoubleBuffer |
                          ControlStyles.ResizeRedraw, true);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = TextRenderingHint.ClearTypeGridFit;

            // Gradient background
            using (LinearGradientBrush brush = new LinearGradientBrush(
                new Rectangle(0, 0, this.Width, this.Height),
                this.darkColor,
                this.lightColor,
                LinearGradientMode.Horizontal))
            {
                g.FillRectangle(brush, 0, 0, this.Width, this.Height);
            }

            // Top vibrant accent highlight line
            using (SolidBrush lineBrush = new SolidBrush(this.accentLineColor))
            {
                g.FillRectangle(lineBrush, 0, 0, this.Width, 3);
            }

            // Logo
            int logoSize = 120;
            int logoLeft = 28;
            int logoTop = 26;
            if (this.logo != null)
            {
                g.InterpolationMode = InterpolationMode.HighQualityBicubic;
                g.DrawImage(this.logo, new Rectangle(logoLeft, logoTop, logoSize, logoSize));
            }

            int textLeft = logoLeft + logoSize + 22;

            // Pill tag
            string tagText = "FAA-COMPLIANT PAVEMENT ENGINEERING SUITE • 2026 EDITION";
            using (Font tagFont = new Font("Segoe UI", 8f, FontStyle.Bold))
            {
                Size tagSize = TextRenderer.MeasureText(tagText, tagFont);
                Rectangle tagRect = new Rectangle(textLeft, 24, tagSize.Width + 14, 22);
                using (GraphicsPath tagPath = LauncherForm.GetRoundedRect(tagRect, 4))
                {
                    using (SolidBrush tagBg = new SolidBrush(Color.FromArgb(40, 255, 255, 255)))
                    {
                        g.FillPath(tagBg, tagPath);
                    }
                }
                TextRenderer.DrawText(g, tagText, tagFont, new Point(textLeft + 7, 27), Color.FromArgb(0, 210, 235),
                    TextFormatFlags.Left | TextFormatFlags.Top | TextFormatFlags.NoPrefix);
            }

            // Main Title
            using (Font titleFont = new Font("Segoe UI", 20f, FontStyle.Bold))
            {
                Rectangle titleRect = new Rectangle(textLeft, 48, this.Width - textLeft - 20, 40);
                TextRenderer.DrawText(g, "AIRPORT FWD DATA ANALYZER", titleFont, titleRect, Color.White,
                    TextFormatFlags.Left | TextFormatFlags.Top | TextFormatFlags.EndEllipsis | TextFormatFlags.NoPrefix);
            }

            // Subtitle
            using (Font subFont = new Font("Segoe UI", 10f, FontStyle.Regular))
            {
                Rectangle subRect = new Rectangle(textLeft, 94, this.Width - textLeft - 20, 24);
                TextRenderer.DrawText(g, "FWD/HWD Deflection Analysis • Layer Moduli Backcalculation • FAA Pavement & Overlay Design",
                    subFont, subRect, Color.FromArgb(200, 225, 245),
                    TextFormatFlags.Left | TextFormatFlags.Top | TextFormatFlags.EndEllipsis | TextFormatFlags.NoPrefix);
            }

            // Author & metadata
            using (Font metaFont = new Font("Segoe UI", 8.8f, FontStyle.Regular))
            {
                Rectangle metaRect = new Rectangle(textLeft, 124, this.Width - textLeft - 20, 22);
                TextRenderer.DrawText(g, "Developed & Packaged by Sahil Yadav • Integrated BAKFAA v3.4.4 & FAARFIELD v2.1.2",
                    metaFont, metaRect, Color.FromArgb(255, 195, 75),
                    TextFormatFlags.Left | TextFormatFlags.Top | TextFormatFlags.EndEllipsis | TextFormatFlags.NoPrefix);
            }

            // Bottom border line
            using (Pen bottomPen = new Pen(Color.FromArgb(40, 0, 0, 0), 1))
            {
                g.DrawLine(bottomPen, 0, this.Height - 1, this.Width, this.Height - 1);
            }
        }
    }
}
