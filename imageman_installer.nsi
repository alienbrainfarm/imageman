; ImageMan NSIS Installer Script
; Requires NSIS (https://nsis.sourceforge.io/)

Name "ImageMan"
OutFile "ImageManSetup.exe"
InstallDir "$PROGRAMFILES\ImageMan"
RequestExecutionLevel admin

Page directory
Page instfiles

; Add installer icon
Icon "ImageMan.ico"

Section "Install"
    SetOutPath "$INSTDIR"
    File "imageman\dist\ImageMan\ImageMan.exe"
    File "ImageMan.ico"
   
    ; Start Menu shortcut
    CreateShortCut "$SMPROGRAMS\ImageMan.lnk" "$INSTDIR\ImageMan.exe" "" "$INSTDIR\ImageMan.ico"
    ; Desktop shortcut (optional, ask user)

    MessageBox MB_YESNO "Create a desktop shortcut?" IDNO noDesktop
    CreateShortCut "$DESKTOP\ImageMan.lnk" "$INSTDIR\ImageMan.exe" "" "$INSTDIR\ImageMan.ico"
noDesktop:

    ; Add 'Open with ImageMan' to directory context menu
    WriteRegStr HKCR "Directory\shell\Open with ImageMan" "" "Open with ImageMan"
    WriteRegStr HKCR "Directory\shell\Open with ImageMan\command" "" '"$INSTDIR\ImageMan.exe" "%1"'
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\ImageMan.exe"
    Delete "$SMPROGRAMS\ImageMan.lnk"
    Delete "$DESKTOP\ImageMan.lnk"
    RMDir "$INSTDIR"
    DeleteRegKey HKCR "Directory\shell\Open with ImageMan"
SectionEnd
