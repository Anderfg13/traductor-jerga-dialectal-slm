# Frases candidatas para la demo (resultados reales)

Generado con `evaluation/probar_frases_demo.py`: modelo desplegado (base Qwen2.5-3B + adaptador de `api/space/adapter`, en CPU, ~1 min por frase) frente a DeepL. **Google Translate no se probó** (no hay clave): pega cada frase en translate.google.com y compara a mano antes de afirmar que falla. Las frases son nuevas, pero usan expresiones del banco de semillas de entrenamiento, así que los aciertos no prueban que generalice a jerga desconocida.

| Dialecto | Frase | Nuestro modelo | DeepL | Veredicto (lectura del autor, no de un nativo) |
|---|---|---|---|---|
| Caribeña | No vayas a dar papaya con el celular en el bus. | Don't be a jerk with your phone on the bus. | Don't make yourself a target by using your cell phone on the bus. | falla nuestro |
| Caribeña | Ese man es un show, se puso a bailar en plena reunión. | That guy is a show, he started dancing in the middle of the meeting. | That guy is quite a character—he started dancing right in the middle of the meeting. | parcial |
| Caribeña | Estoy en la olla, no me alcanza ni para el almuerzo. | I'm in a tight spot, I don't even have enough for lunch. | I'm broke; I can't even afford lunch. | acierta (matiz menor) |
| Andina | Pilas con ese perro que muerde. | Watch out for that dog that bites. | Watch out for that dog—it bites. | ambos bien |
| Andina | Hagamos una vaca para el regalo de Laura. | Let's pool our money for Laura's gift. | Let's make a cow as a gift for Laura. | acierta nuestro; DeepL literal |
| Andina | Ese lleva y trae le contó todo al jefe. | That guy spilled the beans to the boss. | That go-between told the boss everything. | ambos aproximados |
| Rioplatense | Estoy hecho percha, laburé doce horas seguidas. | I'm completely exhausted, I worked for twelve straight hours. | I'm completely wiped out—I worked twelve hours straight. | ambos bien |
| Rioplatense | Ni en pedo te presto la plata de nuevo. | Not a chance I'll lend you the money again. | There's no way in hell I'm lending you money again. | ambos bien |
| Rioplatense | No seas careta, decime la verdad. | Don't be a fake, tell me the truth. | Don't be a hypocrite—tell me the truth. | ambos bien |
| Mexicana | Ponte trucha, que ahorita pasa el camión. | Watch out, the truck is coming right now. | Hurry up—the bus is coming right now. | falla nuestro |
| Mexicana | Estoy crudo, ni me hables hasta mañana. | I'm hungover, don't talk to me until tomorrow. | I'm hungover—don't even talk to me until tomorrow. | ambos bien |
| Mexicana | Está bien gacho que no me hayas avisado. | It's a bit annoying that you didn't tell me. | It's really too bad you didn't let me know. | ambos aproximados |
| Chilena | Ya po, no seai fome y ven a la fiesta. | Come on, don't be hungry and come to the party. | Come on, don't be a bore—come to the party. | falla nuestro ('hungry') |
| Chilena | Anoche lo pasamos la raja, hoy ando con la caña. | Last night we had a blast, today I'm hungover. | We had a blast last night; today I'm feeling a little rough. | ambos bien |
| Chilena | Estoy pato hasta el viernes. | I'm totally broke until Friday. | I'm swamped until Friday. | acierta nuestro; DeepL falla |

## Para la demo

- **Muestran bien:** "Hagamos una vaca para el regalo de Laura." y "Estoy pato hasta el viernes." (DeepL falla en ambas; verificar Google Translate).
- **Muestran el límite (honesto):** "Ya po, no seai fome y ven a la fiesta." y "No vayas a dar papaya con el celular en el bus." (nuestro modelo falla y DeepL acierta).
- En la demo en vivo usar el Space (~2.5 s); en CPU local cada frase tarda ~1 minuto.
