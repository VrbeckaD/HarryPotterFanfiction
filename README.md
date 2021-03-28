# HarryPotterFanfiction

## Motivation

This software was created to support the diploma thesis of Dominika Vrbecká.
Feel free to contact me at 451002@mail.muni.cz.

## Installation

To replicate the experiments from my diploma thesis:

 1. Call `git clone git@github.com:VrbeckaD/HarryPotterFanfiction.git` or download and unpack as `zip`.
 2. Select Python3 virtual environment `source /your/python3/bin/activate`
 3. Install all requirements: `pip install -r requirements.txt`
 4. Download urls with article lists containing links to urls with 
    article contents (first 5000 pages containing links to fandom texts,
    it will take approximately one hour):
    
    ```bash
    python -m hp.download 5000
    ```
    Results will be stored into `downloaded_url_lists` folder.
 5. Download metadata by calling (it will take 12-24 hours):

    ```bash
    python -m hp.metadata_collector
    ```
    Results will be stored into folder `downloaded_fullarticles`.
    Also, csv file `hp/HP_catalogue.csv` will be created with all metadata:
    
    ```csv
    filename,title,rating,ship,language,category,lovers,wordcount,published,hits,freeform_tags
    1_1.txt,The Debauchery of Trust,explicit,none,English,slash,Abraxas Malfoy/Tom Riddle,3919,2020-04-01,1316,Smut|69 (Sex Position)|Blow Jobs|Anal Sex|Anal Fingering|Established Relationship|First War with Voldemort|Sane Voldemort (Harry Potter)|Dom/sub|Sub Tom Riddle|Drunk Sex|Love Confessions|Trust Issues|Dirty Talk
    1_2.txt,Love Inquires,mature,none,English,multi,Aziraphale/Crowley (Good Omens),50371,2020-02-21,1098,Harry Potter was Adopted by Other(s)|Harry Potter was Raised by Other(s)|Hermoine was Adopted by Loki( Gabriel)|Harry&#39;s Paseltounge isn&#39;t just becase of the Horcux becuase come On!|Harry was a Horcux he isn&#39;t anymore thank someone|Lucas Burr the Supernatual dectector|Sam adopts Lucas Burr becuase Lucas is a quite soul who&#39;s family died|Pagen Sam|phinx had a cult( really isn&#39;t one but it&#39;s easist way to say it)|Sam is takeing online courses for something|Adam Milligan is a Winchester|Adam Milligan gouse by Abel Milligan to odvoide confousion with Adam Young|Lucifer Morningstar from Lucifer is Lucifer/ Satan from Good Omens|Lucifer Morningstar is the Real Devil|He has a vauge idea of what is happing|Gabriel (Supernatural) is Loki|So he has some kidos other then Hermoine|Hermoine Granger is Hermoine Granger-Lokidótti|Marryed Crowley and Aziraphale|Good Parents Aziraphale and Crowley (Good Omens)|Anathema and Newton have adopted Warlock on the wishes of Nany Ashthron|Warlock is a warlock( Read Wizeard)|BAMF Luna Lovegood|Seer Luna Lovegood|Realy it&#39;s BAMF everyone|Oh Look Newt and Creadnce were friends with Crowley|Oh Look! Demon deals aren&#39;t the only one in the clouset|This is LBGT+ friendly|I wrote this instead of sleeping on muliple occasions|I pritty sure my grades are suffering becuase of this|Most parts are over 3000 words|Season 3 sorta rewright|Season 4 sorta rewright|There is alot of cris crossing|do try and keep up|Headcanon Sam had a wonderfull Singing voice|Someone help these people|Sammy had powers not ashoiated with Demon blood|Demon blood? what Demon Blood|Weasleys&#39; Wizard Wheezes|Weasley Bashing|Exept Fred George Bill Charlie and Percy|Werewolf! Bill Weasley|Asexual Charlie Weasley|Magical Stiles Stilinski|Pre-Season/Series 01|Canon Divergence - Post-Harry Potter and the Deathly Hallows|Canon Divergence - Pre-Harry Potter and the Deathly Hallows|Death in good Omens is Death in Superntatural|Pestilence is Pollotions twin|Famine (Good Omens) is Famine (supernatual) Ward|War (supernatual) is War( Good Omens) husband|Smart Sam Winchester|Arrowverse timeline with a few changes becase it&#39;s not very spific with some events|Arrowverse Crossover|Once again you can&#39;t have Constientin with out Green Arrow|Wrote this before I even learned of Crist on ifenent earths|Pre- Canon for most Arrowverse|Pre-Crisis|Mettions of the Bat Family|This sires is now Chaotic Lawfull|Constinetin had a one night stand with Lucifer at one point|Crowley and Jörmungandr are Gender-fluid and no one can fight me on that|Creation of the Time Masters? Hells yeah I did|Time Master created becuase of the Professor and Rose Tyler|Time Masters created by a Timelord|Mettions of Sandbrook|Uriel (supernatual) is Uriel (Good Omens)|Micheal ( Good Omens) is Micheal (Supernatural)|The Holmes childern are half timelord|Gabriel( Good Omens) is a Clone of Gabriel( Supernatural) Crated by Ralpheal and Micheal|Angels Demons and Werewolves have mates|Jimmy is a single parent|Who gets Cas to take in his daughter while wearing him like a prom dress|The Best Baby sitter is Hela the Goddess of the unhonerble dead|Lucas and Claire are BAF BFF|Castiel adopts Claire Novek|Severus is helping stop the Apocuilipes becuase he is board|Windigo Hannibal Lector|Ravenstag|No beta we fall like Crowley|Ravenstag Will Graham|Ravenstag Hannibal Lector|Will Graham and Dean Winchester were penpals of Sorts|Master of Death Harry Potter|Mpreg|Eventualy|Magial Beverly Katz|Adam Young Still Has Powers (Good Omens)
    ```
    
    Not all url lists defined in `downloaded_url_lists` are always successful, in our case,
    1821 of url lists weren't successfully processed and we obtained only 63600 records.
    
    