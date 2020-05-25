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

Function GetFilterOrderID() As String
'Prompts user for Order ID input for Amazon export txt file orders filtering
Dim HelperDialogText As String

HelperDialogText = "Enter Amazon order-id from which you want to export orders" & vbCrLf & vbCrLf & "Leave blank to export all orders"
OrderID = InputBox(HelperDialogText, "Enter Order-ID")
If OrderID = "" Then
    GetFilterOrderID = ""
    Exit Function
Else
    GetFilterOrderID = OrderID
    Exit Function
End If
End Function
