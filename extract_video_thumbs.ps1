Add-Type -AssemblyName System.Drawing
$code = @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
using System.Drawing.Imaging;

[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("bcc18b79-ba16-442f-80c4-8a59c30c463b")]
interface IShellItemImageFactory {
  void GetImage(SIZE size, SIIGBF flags, out IntPtr phbm);
}

[StructLayout(LayoutKind.Sequential)]
struct SIZE {
  public int cx;
  public int cy;
  public SIZE(int x, int y) { cx = x; cy = y; }
}

[Flags]
enum SIIGBF {
  ResizeToFit = 0x00,
  BiggerSizeOk = 0x01,
  MemoryOnly = 0x02,
  IconOnly = 0x04,
  ThumbnailOnly = 0x08,
  InCacheOnly = 0x10,
  CropToSquare = 0x20,
  WideThumbnails = 0x40,
  IconBackground = 0x80,
  ScaleUp = 0x100
}

public static class ThumbUtil {
  [DllImport("shell32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
  static extern void SHCreateItemFromParsingName(string path, IntPtr pbc, [MarshalAs(UnmanagedType.LPStruct)] Guid riid, out IShellItemImageFactory item);
  [DllImport("gdi32.dll")]
  static extern bool DeleteObject(IntPtr hObject);

  public static void Save(string path, string output, int size) {
    IShellItemImageFactory factory;
    var iid = new Guid("bcc18b79-ba16-442f-80c4-8a59c30c463b");
    SHCreateItemFromParsingName(path, IntPtr.Zero, iid, out factory);
    IntPtr hbitmap;
    factory.GetImage(new SIZE(size, size), SIIGBF.ThumbnailOnly | SIIGBF.BiggerSizeOk, out hbitmap);
    using (var bmp = Image.FromHbitmap(hbitmap)) {
      bmp.Save(output, ImageFormat.Png);
    }
    DeleteObject(hbitmap);
  }
}
"@
Add-Type -TypeDefinition $code -ReferencedAssemblies System.Drawing

$root = 'C:\Users\21407\Desktop\claude code\files\skicheck\public\demo-candidates'
$outRoot = 'C:\Users\21407\Desktop\ski\demo_thumbs'
New-Item -ItemType Directory -Force -Path $outRoot | Out-Null

Get-ChildItem -LiteralPath $root -Filter *.mp4 | ForEach-Object {
  $out = Join-Path $outRoot ($_.BaseName + '.png')
  [ThumbUtil]::Save($_.FullName, $out, 512)
  Write-Output $out
}
