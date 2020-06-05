Attribute VB_Name = "Functions"
Function GetTXTFile() As Variant

Dim ReturnVal As String
Dim fd As FileDialog
Dim ActionClicked As Boolean

'Initializing file picker dialogbox
Set fd = Application.FileDialog(msoFileDialogFilePicker)
fd.AllowMultiSelect = False
fd.Title = "Select Codes TXT file"
fd.InitialFileName = ThisWorkbook.Path
fd.Filters.Clear
fd.Filters.Add "TXT Files Only", "*.txt"

ActionClicked = fd.Show

'End program if user cancelled
If ActionClicked Then
    GetTXTFile = fd.SelectedItems(1)
    Exit Function
Else
    'user cancelled - ending program
    End
End If

ReturnVal = fd.SelectedItems(1)

'Returning value:
GetTXTFile = ReturnVal

End Function
