# C9 — Microsoft Graph CLI Quick Reference

U.S. Energy Developer AI Training · Session 2 (Hour 4) reference

Commands for email, Teams, and SharePoint using the `Microsoft.Graph` PowerShell module distributed to attendees. All commands run in **PowerShell 7**.
---

## Authentication

```powershell
# Connect interactively (browser prompt)
Connect-MgGraph -Scopes "Mail.Read","Mail.Send","ChannelMessage.Send","Files.Read.All","Sites.Read.All"

# Check who you're connected as
Get-MgContext

# Disconnect
Disconnect-MgGraph
```

> Add only the scopes you need. More scopes = broader permissions = more to explain to IT.

---

## Email

### List recent emails (inbox, last 10)

```powershell
Get-MgUserMessage -UserId "me" -Top 10 |
    Select-Object Subject, ReceivedDateTime, @{N="From";E={$_.From.EmailAddress.Address}}
```

### Search emails by subject

```powershell
Get-MgUserMessage -UserId "me" -Filter "contains(subject,'IFTA')" -Top 20 |
    Select-Object Subject, ReceivedDateTime
```

### Read the body of a specific email

```powershell
# Get the message ID first, then retrieve the full body
$msg = Get-MgUserMessage -UserId "me" -MessageId "<message-id>"
$msg.Body.Content
```

### Send an email

```powershell
$params = @{
    Message = @{
        Subject = "Test from PowerShell"
        Body = @{
            ContentType = "Text"
            Content = "Sent via Microsoft Graph CLI."
        }
        ToRecipients = @(
            @{ EmailAddress = @{ Address = "colleague@usventureenv.com" } }
        )
    }
    SaveToSentItems = $true
}
Send-MgUserMail -UserId "me" -BodyParameter $params
```

---

## Teams

### List teams you're a member of

```powershell
Get-MgUserJoinedTeam -UserId "me" | Select-Object DisplayName, Id
```

### List channels in a team

```powershell
Get-MgTeamChannel -TeamId "<team-id>" | Select-Object DisplayName, Id
```

### Post a message to a channel

```powershell
$params = @{
    Body = @{
        Content = "Hello from PowerShell via Microsoft Graph."
    }
}
New-MgTeamChannelMessage -TeamId "<team-id>" -ChannelId "<channel-id>" -BodyParameter $params
```

---

## SharePoint / OneDrive

### List SharePoint sites

```powershell
Get-MgSite -Search "logbook" | Select-Object DisplayName, WebUrl, Id
```

### List document libraries (drives) on a site

```powershell
Get-MgSiteDrive -SiteId "<site-id>" | Select-Object Name, Id
```

### List files in a document library

```powershell
Get-MgDriveItem -DriveId "<drive-id>" -DriveItemId "root" |
    Select-Object Name, LastModifiedDateTime
```

### Download a file

```powershell
# Get the download URL, then fetch the file
$item = Get-MgDriveItem -DriveId "<drive-id>" -DriveItemId "<item-id>" -Property "@microsoft.graph.downloadUrl"
Invoke-WebRequest -Uri $item.AdditionalProperties["@microsoft.graph.downloadUrl"] -OutFile "localfile.xlsx"
```

---

## Finding IDs

Many commands need a `TeamId`, `ChannelId`, `SiteId`, or `DriveId`. Quick ways to find them:

```powershell
# Teams and channels
Get-MgUserJoinedTeam -UserId "me" | Select-Object DisplayName, Id
Get-MgTeamChannel -TeamId "<team-id>" | Select-Object DisplayName, Id

# Sites
Get-MgSite -Search "<keyword>" | Select-Object DisplayName, Id
```

---

## Tips for AI-Assisted Work

- **Store IDs in .env.** Put `TEAMS_CHANNEL_ID`, `SHAREPOINT_SITE_ID`, etc. in `.env` so Claude Code can reference them without asking. The agent reads `$env:TEAMS_CHANNEL_ID`; it doesn't need to look it up every session.
- **Wrap repeated calls in a function.** If you post to the same Teams channel every day, wrap `New-MgTeamChannelMessage` in a function with the IDs baked in.
- **Ask Claude Code to write the wrapper.** Give it the raw command and the parameters, and ask for a named PowerShell function. That function is now a "Make Correctness Easy" asset.
