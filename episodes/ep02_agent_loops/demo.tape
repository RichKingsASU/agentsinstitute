# Token cascade without guards, then the repeat guard stopping it. Render: python pipeline/generator.py ep02_agent_loops
Set Shell "powershell"
Set FontFamily "JetBrains Mono"
Set FontSize 30
Set Width 1920
Set Height 1080
Set Padding 40
Set Framerate 30
Set PlaybackSpeed 1.0
Set TypingSpeed 40ms
Set Theme { "name": "AgentsInstitute", "background": "#0B0F19", "foreground": "#F1F5F9", "cursor": "#00F0FF", "selection": "#151C2C", "black": "#0B0F19", "red": "#FF5C7A", "green": "#00F0FF", "yellow": "#FACC15", "blue": "#7000FF", "magenta": "#A78BFA", "cyan": "#00F0FF", "white": "#F1F5F9", "brightBlack": "#94A3B8", "brightRed": "#FF5C7A", "brightGreen": "#5EEAD4", "brightYellow": "#FDE047", "brightBlue": "#8B5CF6", "brightMagenta": "#C4B5FD", "brightCyan": "#67E8F9", "brightWhite": "#FFFFFF" }

Hide
Type "cls" Enter
Show

Type "python counter_agent.py --no-guards" Sleep 300ms Enter
Sleep 6s
Type "python counter_agent.py" Sleep 300ms Enter
Sleep 8500ms
