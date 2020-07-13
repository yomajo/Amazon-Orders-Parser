Attribute VB_Name = "ParseAmazonOrders"
Dim objShell As Object
Dim objExec As Object
Dim objOutput As Object
Dim oCmd As String
Dim sOutputStr As String
Dim sLine As String

Dim OrderID As String
Dim PythonScriptExe As String
Dim TxtFilePath As Variant


Sub ExportAmazonOrders()
' Main method on button click

Application.ScreenUpdating = False

'Setting variables
PythonScriptExe = ThisWorkbook.Path & "\Helper" & " " & "Files\main_amazon.exe"

'Open dialog box to pick txt file for parsing (check if exists)
TxtFilePath = GetTXTFile

'Open shell with stdout listening, execute py script, pass along picked txt file, filtering orderID value
'Handling of errors and completion messages inside sub-module:
Call ParseAmazonWithPython(PythonScriptExe, TxtFilePath)

Application.ScreenUpdating = True
End Sub

Sub ParseAmazonWithPython(PythonScriptExe As String, TxtFilePath As Variant)
'Wrapper function to launch compiled python executable (.exe) parser (with provided args and listen to Py output in console

'Reset variable
sOutputStr = ""

'Cmd command to be executed:
oCmd = """" & PythonScriptExe & """" & " " & """" & TxtFilePath & """"

'Creating and start shell:
Set objShell = VBA.CreateObject("Wscript.Shell")
Set objExec = objShell.Exec(oCmd)
Set objOutput = objExec.StdOut

'Reading output
While Not objOutput.AtEndOfStream
    sLine = objOutput.ReadLine
    If sLine <> "" Then sOutputStr = sOutputStr & sLine & vbCrLf
Wend
Debug.Print sOutputStr

'Resetting objects
Set objOutput = Nothing
Set objExec = Nothing
Set objShell = Nothing

'No new orders provided with OrderID case
If InStr(1, sOutputStr, "NO NEW JOB") > 0 Then
    MsgBox "All orders in file '" & Dir(TxtFilePath) & "' have been processed already", vbInformation, "No new Amazon Orders"
    Exit Sub
End If

'Handling errors
If InStr(1, sOutputStr, "ERROR_CALL_DADDY") > 0 Then
    MsgBox "Encountered error while reading source file or creating outputs" & vbCrLf & vbCrLf & "Send '" & Dir(TxtFilePath) & "' and 'loading_amazon_orders.log' from Helper Files to:" & vbCrLf & "ed.vinas@yahoo.com", vbCritical, "Error Handling Amazon Orders"
    Exit Sub
ElseIf InStr(1, sOutputStr, "ETONAS_CHARLIMIT_WARNING") > 0 Then
    MsgBox "One or more orders in Etonas export excel file address columns contains more than 32 symbols." & vbCrLf & vbCrLf & "Rearrange before sending a file", vbInformation, "Etonas Address cell limit exceeded"
End If

'Check for DPost warning
If InStr(1, sOutputStr, "DPOST_CHARLIMIT_WARNING") > 0 Then
    MsgBox "One or more orders in Deutsche Post exceed field limits. Rearrange name or address fields", vbInformation, "Deutsche Post field(s) exceeded limit"
End If

'Check for key(headers) error:
If InStr(1, sOutputStr, "ERROR_IN_SOURCE_HEADERS") > 0 Then
    MsgBox "Could not find anticipated headers in source file." & vbCrLf & vbCrLf & "Check Amazon export settings or changes in export file headers", vbCritical, "Error Handling Amazon Orders"
    Exit Sub
End If

'Check for Success:
If InStr(1, sOutputStr, "EXPORTED_SUCCESSFULLY") > 0 Then
    MsgBox "Orders successfully exported! Check:" & vbCrLf & vbCrLf & ThisWorkbook.Path, vbInformation, "Amazon Orders Proccessed"
End If

End Sub
