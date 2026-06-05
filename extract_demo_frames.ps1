Add-Type -AssemblyName PresentationCore,WindowsBase

$root = 'C:\Users\21407\Desktop\claude code\files\skicheck\public\demo-candidates'
$outRoot = 'C:\Users\21407\Desktop\ski\demo_frames'
New-Item -ItemType Directory -Force -Path $outRoot | Out-Null

$files = @(
  '2990586685b77e33e678c213397848b9.mp4',
  'c4b49df73a567d4580c0b821dfc480e1.mp4',
  'f7dfa83364e5ac4d7e2d719482d484c9.mp4',
  '4dc05667064b40a321d73815149a1279.mp4'
)

function Pump($ms) {
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while ($sw.ElapsedMilliseconds -lt $ms) {
    [Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([Action]{}, [Windows.Threading.DispatcherPriority]::Background)
    Start-Sleep -Milliseconds 50
  }
}

foreach ($file in $files) {
  $video = Join-Path $root $file
  $player = New-Object System.Windows.Media.MediaPlayer
  $script:opened = $false
  $script:failed = $null
  $player.add_MediaOpened({ $script:opened = $true })
  $player.add_MediaFailed({ param($s, $e) $script:failed = $e.ErrorException.Message })
  $player.Open([Uri]::new($video))
  Pump 5000
  if (-not $script:opened -or $script:failed) {
    Write-Output "SKIP $file $script:failed"
    continue
  }
  $dur = $player.NaturalDuration.TimeSpan.TotalSeconds
  $w = [int]$player.NaturalVideoWidth
  $h = [int]$player.NaturalVideoHeight
  Write-Output "$file $w x $h dur=$dur"
  foreach ($ratio in @(0.25, 0.5, 0.75)) {
    $t = [math]::Max(0.1, [math]::Min($dur - 0.1, $dur * $ratio))
    $player.Pause()
    $player.Position = [TimeSpan]::FromSeconds($t)
    Pump 1200
    $dv = New-Object System.Windows.Media.DrawingVisual
    $dc = $dv.RenderOpen()
    $dc.DrawVideo($player, [System.Windows.Rect]::new(0, 0, $w, $h))
    $dc.Close()
    $rtb = New-Object System.Windows.Media.Imaging.RenderTargetBitmap($w, $h, 96, 96, [System.Windows.Media.PixelFormats]::Pbgra32)
    $rtb.Render($dv)
    $enc = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
    $enc.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($rtb))
    $base = [IO.Path]::GetFileNameWithoutExtension($file)
    $out = Join-Path $outRoot ("${base}_$([int]($ratio * 100)).png")
    $fs = [IO.File]::Create($out)
    $enc.Save($fs)
    $fs.Close()
    Write-Output "  $out"
  }
  $player.Close()
}
