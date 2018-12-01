#!/usr/bin/python3
import datetime
import sys
import argparse
import odf
import odf.opendocument
import odf.style
import odf.text
import odf.table
import odf.draw
import odf.meta
import odf.dc
import os

_=str
version="20140417"
class Mem:
    def __init__(self):
        self.ways=SetWays(self).load()
        self.categories=SetCategories(self).load()
        self.languages=SetLanguages(self).load()
        self.publishers=SetPublishers(self).load()
        
        self.games=SetGames(self).load()



class ODT:
    def __init__(self, mem, filename, template=None):    
        self.mem=mem
        self.filename=filename
        self.doc=odf.opendocument.OpenDocumentText()
        
        if template!=None:
            templatedoc= odf.opendocument.load(template)
            for style in templatedoc.styles.childNodes[:]:
                self.doc.styles.addElement(style)
          
            for autostyle in templatedoc.automaticstyles.childNodes[:]:
                self.doc.automaticstyles.addElement(autostyle)
                
            for master in templatedoc.masterstyles.childNodes[:]:
                self.doc.masterstyles.addElement(master)
                
        #Pagebreak styles horizontal y vertical        
        s = odf.style.Style(name="PH", family="paragraph",  parentstylename="Standard", masterpagename="Landscape")
        s.addElement(odf.style.ParagraphProperties(pagenumber="auto"))
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"2pt",'fontweight':"bold" }, ))
        self.doc.styles.addElement(s)
        s = odf.style.Style(name="PV", family="paragraph",  parentstylename="Standard", masterpagename="Standard")
        s.addElement(odf.style.ParagraphProperties(pagenumber="auto"))
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"2pt",'fontweight':"bold" }))
        self.doc.styles.addElement(s)
        
        
            
        self.seqTables=0#Sequence of tables
        
    def emptyParagraph(self, style="Standard", number=1):
        for i in range(number):
            self.simpleParagraph("",style)
            
    def simpleParagraph(self, text, style="Standard"):
        p=odf.text.P(stylename=style, text=text)
        self.doc.text.addElement(p)
        
    def header(self, text, level):
        h=odf.text.H(outlinelevel=level, stylename="Heading {}".format(level), text=text)
        self.doc.text.addElement(h)
        
        
        
    def table(self, header, orientation,  data, sizes, font):
        """Headerl text
        Data: data
        sizes: arr with column widths in cm
        size=font size"""  
    
        self.seqTables=self.seqTables+1
        tablesize=sum(sizes)
        
        s=odf.style.Style(name="Tabla{}".format(self.seqTables))
        s.addElement(odf.style.TableProperties(width="{}cm".format(tablesize), align="center"))
        self.doc.automaticstyles.addElement(s)
        
        #Column sizes
        for i, size in enumerate(sizes):
            sc= odf.style.Style(name="Tabla{}.{}".format(self.seqTables, chr(65+i)), family="table-column")
            sc.addElement(odf.style.TableColumnProperties(columnwidth="{}cm".format(sizes[i])))
            self.doc.automaticstyles.addElement(sc)
        
        #Cell header style
        sch=odf.style.Style(name="Tabla{}.HeaderCell".format(self.seqTables, chr(65), 1), family="table-cell")
        sch.addElement(odf.style.TableCellProperties(border="0.05pt solid #000000"))
        self.doc.automaticstyles.addElement(sch)        
        
        #Cell normal
        sch=odf.style.Style(name="Tabla{}.Cell".format(self.seqTables), family="table-cell")
        sch.addElement(odf.style.TableCellProperties(border="0.05pt solid #000000"))
        self.doc.automaticstyles.addElement(sch)
        
        
        #TAble contents style
        
        s= odf.style.Style(name="Tabla{}.Heading{}".format(self.seqTables, font), family="paragraph",parentstylename='Table Heading' )
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        s.addElement(odf.style.ParagraphProperties(attributes={'textalign':'center', }))
        self.doc.styles.addElement(s)
        
        s = odf.style.Style(name="Tabla{}.TableContents{}".format(self.seqTables, font), family="paragraph")
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        self.doc.styles.addElement(s)
        
        s = odf.style.Style(name="Tabla{}.TableContentsRight{}".format(self.seqTables, font), family="paragraph")
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font), }))
        s.addElement(odf.style.ParagraphProperties(attributes={'textalign':'end', }))
        self.doc.styles.addElement(s)
        
        
        
        
        #Table header style
        s = odf.style.Style(name="Tabla{}.HeaderCell{}".format(self.seqTables, font), family="paragraph")
        s.addElement(odf.style.TextProperties(attributes={'fontsize':"{}pt".format(font+1),'fontweight':"bold" }))
        self.doc.styles.addElement(s)
        
        
    
        #Table columns
        table = odf.table.Table(stylename="Tabla{}".format(self.seqTables))
        for i, head in enumerate(header):
            table.addElement(odf.table.TableColumn(stylename="Tabla{}.{}".format(self.seqTables, chr(65+i))))  
            
            
            
        #Header rows
        headerrow=odf.table.TableHeaderRows()
        tablerow=odf.table.TableRow()
        headerrow.addElement(tablerow)
        for i, head in enumerate(header):
            p=odf.text.P(stylename="Tabla{}.Heading{}".format(self.seqTables, font), text=head)
            tablecell=odf.table.TableCell(stylename="Tabla{}.HeaderCell{}".format(self.seqTables, font))
            tablecell.addElement(p)
            tablerow.addElement(tablecell)
        table.addElement(headerrow)
            
        #Data rows
        for row in data:
            tr = odf.table.TableRow()
            table.addElement(tr)
            for i, col in enumerate(row):
                tc = odf.table.TableCell(stylename="Tabla{}.Cell".format(self.seqTables))
                tr.addElement(tc)
                
                #Parses orientation
                if orientation[i]=="<":
                    p = odf.text.P(stylename="Tabla{}.TableContents{}".format(self.seqTables, font))
                elif orientation[i]==">":
                    p = odf.text.P(stylename="Tabla{}.TableContentsRight{}".format(self.seqTables, font))
                
                #Colorize numbers less than zero
                try:#Formato 23 €
                    if float(col.split(" ")[0])<0:
                        s=odf.text.Span(text=col, stylename="Rojo")
                    else:
                        s=odf.text.Span(text=col)
                except:
                    s=odf.text.Span(text=col)                    
                p.addElement(s)
                
                tc.addElement(p)
        
        self.doc.text.addElement(table)
        
    def image(self, filename, width, height):
        p = odf.text.P(stylename="Illustration")
        href = self.doc.addPicture(filename)
        f = odf.draw.Frame(name="filename", anchortype="as-char", width="{}cm".format(width), height="{}cm".format(height)) #, width="2cm", height="2cm", zindex="0")
        p.addElement(f)
        img = odf.draw.Image(href=href, type="simple", show="embed", actuate="onLoad")
        f.addElement(img)
        self.doc.text.addElement(p)
    
    def image_arr(self, arrfilename, width, height):
        """Images arr in a paragraph"""
        p = odf.text.P(stylename="Illustration")
        for i, file in enumerate(arrfilename):
            href = self.doc.addPicture(file)
            f = odf.draw.Frame(name="filename", anchortype="as-char", width="{}cm".format(width), height="{}cm".format(height)) #, width="2cm", height="2cm", zindex="0")
            p.addElement(f)
            img = odf.draw.Image(href=href, type="simple", show="embed", actuate="onLoad")
            f.addElement(img)
            if i<len(arrfilename)-1:#To avoid space in last image
                s=odf.text.Span(text=" ")                    
                p.addElement(s)
        self.doc.text.addElement(p)
        
        
    def image_paragraph(self, filename, width, height, text):
        """If filename is None muestra solo el texto"""
        p = odf.text.P(stylename="Standard")
        if filename:
            href = self.doc.addPicture(filename)
            f = odf.draw.Frame(name="filename", anchortype="as-char", width="{}cm".format(width), height="{}cm".format(height)) #, width="2cm", height="2cm", zindex="0")
            p.addElement(f)
            img = odf.draw.Image(href=href, type="simple", show="embed", actuate="onLoad")
            f.addElement(img)
            s=odf.text.Span(text=" ")                    
            p.addElement(s)
        s=odf.text.Span(text=text)                    
        p.addElement(s)
        self.doc.text.addElement(p)

    def pageBreak(self,  horizontal=False):    
#        p=odf.text.P(stylename="PageBreak")#Is an automatic style
#        self.doc.text.addElement(p)
        if horizontal==True:
            p=odf.text.P(stylename="PH")
        else:
            p=odf.text.P(stylename="PV")
        self.doc.text.addElement(p)
#
#    def link(self):
#        para = odf.text.P()
#        anchor = odf.text.A(href="http://www.com/", text="A link label")
#        para.addElement(anchor)
#        self.doc.text.addElement(para)
#        
#    #######################################

class GamesReport(ODT):
    def __init__(self, mem, filename, template):
        ODT.__init__(self, mem, filename, template)
        self.dir=None#Directory in tmp
        
    def generate(self):
#        self.dir='/tmp/GamesReport-{}'.format(datetime.datetime.now())
#        os.makedirs(self.dir)
        self.variables()
        self.metadata()
        self.cover()
        self.body()
        self.doc.save(self.filename)   
        
    def variables(self):
        pass


    def cover(self):
        self.emptyParagraph(number=10)
        self.simpleParagraph("Games Report", "Title")
        self.simpleParagraph("Generated by Games Report", "Subtitle")
        self.emptyParagraph(number=8)
        self.simpleParagraph("{}".format(datetime.datetime.now()), "Quotations")        
        self.pageBreak()
        
    def body(self):
        self.header(_("Games by name"), 1)
        self.mem.games.sort_by_name()
        for g in self.mem.games.arr:
            # Son necesarias las dos
            self.header(_(g.title), 2)
            if g.cover!=None: 
                self.image(g.cover, 6, 6)
            
            self.header(_("Information"), 3)
            if g.publisher.id!=0 and g.year!=-1:
                self.simpleParagraph(_("This game was published by {0} in {1}.").format(g.publisher.name,g.year))
            
            if g.wished==False:
                if g.origin=="Steam":
                    self.simpleParagraph(_("I own this game because I bought it in Steam."))
                elif g.origin=="Original":
                    self.simpleParagraph(_("I own the original device of this game."))
                elif g.origin=="Downloaded":
                    self.simpleParagraph(_("I downloaded this game from Internet."))
            else:
                self.simpleParagraph(_("I don't own this game, but it's marked as wished."))
                
            if g.valoration!=0:
                self.simpleParagraph(_("This game has a valoration of {} %.").format(g.valoration))
                
            if g.working==True:
                self.simpleParagraph(_("This game is working correctly."))
            else:
                self.simpleParagraph(_("This game is not working."))
                
            
            if len(g.screenshots)>0:
                self.header(_("Screenshots"), 3)     
                arr=[]
                for i, s in enumerate(g.screenshots):
                    arr.append(s)
                    if len(arr)==3 or i==len(g.screenshots)-1:   
                        self.image_arr(arr, 4, 4)
                        arr=[]
    
            if g.experience!="":
                self.header(_("Experience"), 3)  
                for l in g.experience.split("\n"):
                    self.simpleParagraph(l)
            self.pageBreak()
    
        # ORDENADAS ALFABETICAMENTE
        self.header(_("Games in alphabetical order"), 1)
        self.mem.games.sort_by_name()
        for i,g in enumerate(self.mem.games.arr):
            self.image_paragraph(g.cover, 2, 2, g.title)
        self.pageBreak()
                
    
        # ORDENADAS AÑO
        self.header(_("Games by year"), 1)
        tmpyear=-2
        mem.games.sort_by_year()
        for i,g in enumerate(mem.games.arr):
            if tmpyear!=g.year:
                if g.year==-1:
                    self.header(_("Year unknown"), 2)   
                else:
                    self.header(_(g.year), 2)    
                tmpyear=g.year
            self.image_paragraph(g.cover, 2, 2, g.title)
        self.pageBreak()
    
        # ORDENADAS valoration
        self.header(_("Games sorted by its valoration"), 1)
        tmp=-1
        mem.games.sort_by_publisher()
        for i,g in enumerate(mem.games.arr):
            if g.valoration!=0:
                if tmp!=g.valoration:
                    self.header("{} %".format(g.valoration), 2)
                    tmp=g.valoration
                self.image_paragraph(g.cover, 2, 2, g.title)
        self.pageBreak()
        
        # ORDENADAS PUBLISHER
        self.header(_("Games sorted by publisher"), 1)
        tmp="tmp"
        mem.games.sort_by_publisher()
        for i,g in enumerate(mem.games.arr):
            if tmp!=g.publisher.name:
                self.header(g.publisher.name, 2)
                tmp=g.publisher.name
            self.image_paragraph(g.cover, 2, 2, g.title)
        self.pageBreak()
                
        #  GAMES STATE
        self.header(_("Games state"), 1)
        
        self.header(_("Original games"), 2)
        mem.games.sort_by_name()
        for i,g in enumerate(mem.games.arr):
            if g.origin=="Original" or g.origin=="Steam":
                self.image_paragraph(g.cover, 2, 2, "'{}': {}.".format(g.title, g.origin))
                
        self.header(_("Running games"), 2)
        mem.games.sort_by_name()
        for i,g in enumerate(mem.games.arr):
            if g.working==True:
                self.image_paragraph(g.cover, 2, 2, "'{}': {}.".format(g.title, g.origin))
                
        self.header(_("Not running games"), 2)
        mem.games.sort_by_name()
        for i,g in enumerate(mem.games.arr):
            if g.working==False:
                self.image_paragraph(g.cover, 2, 2, "'{}': {}. Last try was on {}.".format(g.title, g.origin, g.norundate))
                
        self.header(_("Not tested games"), 2)
        mem.games.sort_by_name()
        for i,g in enumerate(mem.games.arr):
            if g.working==None:
                self.image_paragraph(g.cover, 2, 2, "'{}': {}.".format(g.title, g.origin))        
        
        self.header(_("Wished games"), 2)
        mem.games.sort_by_name()
        for i,g in enumerate(mem.games.arr):
            if g.wished==True:
                self.image_paragraph(g.cover, 2, 2, g.title)
        self.pageBreak()
        
        
    def metadata(self):
        self.doc.meta.addElement(odf.dc.Title(text="Games report"))
        self.doc.meta.addElement(odf.dc.Description(text="This is an automatic generated report from Games Report"))
        creator="Games Report"
        self.doc.meta.addElement(odf.meta.InitialCreator(text=creator))
        self.doc.meta.addElement(odf.dc.Creator(text=creator))

class Publisher:
    def __init__(self,mem,id,name):
        self.id=id
        self.mem=mem
        self.name=name

class SetPublishers:
    def __init__(self,mem):
        self.mem=mem
        self.arr=[]
    def load(self):
        self.arr.append(Publisher(self.mem,0,"Desconocido"))
        self.arr.append(Publisher(self.mem,1,"Lucas Arts"))
        self.arr.append(Publisher(self.mem,2,"Electronic Arts"))
        self.arr.append(Publisher(self.mem,3,"FX Interactive"))
        self.arr.append(Publisher(self.mem,4,"Ocean"))
        self.arr.append(Publisher(self.mem,5,"THC"))
        self.arr.append(Publisher(self.mem,6,"Ubisoft"))
        self.arr.append(Publisher(self.mem,7,"Bethesda Softworks"))
        self.arr.append(Publisher(self.mem,8,"Zeta Multimedia"))
        
        return self
    def find (self,id):
        for a in self.arr:
            if a.id==id:
                return a
        print ("Publisher not found")
        return self.find(0)

class Category:
    def __init__(self,mem,id,name):
        self.id=id
        self.mem=mem
        self.name=name

class SetCategories:
    def __init__(self,mem):
        self.mem=mem
        self.arr=[]
    def load(self):
        self.arr.append(Category(self.mem,1,"Aventura gráfica"))
        self.arr.append(Category(self.mem,2,"3D shooter"))
        self.arr.append(Category(self.mem,3,"RPG"))
        return self
    def find (self,id):
        for a in self.arr:
            if a.id==id:
                return a
        print ("Category not found")
        return None

class Language:
    def __init__(self,mem,id,name):
        self.id=id
        self.mem=mem
        self.name=name

class SetLanguages:
    def __init__(self,mem):
        self.mem=mem
        self.arr=[]
    def load(self):
        self.arr.append(Language(self.mem,"es","Spanish"))
        self.arr.append(Language(self.mem,"en","English"))
        return self
        
    def find (self,id):
        for a in self.arr:
            if a.id==id:
                return a
        print ("Language not found", id)
        return None
class Way:
    def __init__(self,mem,id,name):
        self.id=id
        self.mem=mem
        self.name=name

class SetWays:
    def __init__(self,mem):
        self.mem=mem
        self.arr=[]
    def load(self):
        self.arr.append(Way(self.mem,1,"Linux native"))
        self.arr.append(Way(self.mem,2,"Wine"))
        self.arr.append(Way(self.mem,3,"Scuumvm"))
        self.arr.append(Way(self.mem,4,"Spectrum"))
        self.arr.append(Way(self.mem,5,"Windows native"))
        return self
    def find (self,id):
        for a in self.arr:
            if a.id==id:
                return a
        print ("Way not found")
        return None

class MyWay:
    def __init__(self,mem,way,works):
        self.mem=mem
        self.way=way
        self.works=works

class SetMyWays:
    def __init__(self,mem):
        self.mem=mem
        self.arr=[]
    def load(self):
        pass

    def find (self,id):
        for a in self.arr:
            if a.way.id==id:
                return a
        print ("MyWay not found")
        return None
        

class Game:
    def __init__(self,mem,id,dir):
        self.id=id#Numero secuenciazl
        self.dir=dir
        self.mem=mem
        self.norundate=None
        self.title=self.find_title()
        self.origin=self.find_origin()
        (self.publisher,self.year)=self.find_publisher_year()
        self.categories=self.find_categories()
        self.languages=self.find_languages()
        self.myways=SetMyWays(self.mem)
        self.cover=self.find_cover()#Relative path
        self.screenshots=self.find_screenshots()#arr with relative paths
        self.experience=self.find_experience()
        self.working=self.find_working()
        self.valoration=self.find_valoration()
        self.wished=self.find_wished()

    def find_cover(self):
        path=self.dir+"/Cover.jpg"
        if os.path.exists(path):
            return path
        return None

    def find_screenshots(self):
        res=[]
        for d in os.listdir(self.dir):
            if d.find("Screenshot")!=-1:
                res.append(self.dir+"/"+d)
        return res


    def find_title(self):
        titlepath=self.dir+"/Title.txt"
        if os.path.exists(titlepath):
            f=open(titlepath)
            name=f.readline()
            f.close()
        else:
            name=os.path.basename(self.dir)
        return name

    def find_origin(self):
        """Can be Steam|Original|Downloaded"""
        res="Downloaded"
        path=self.dir+"/Original.txt"
        if os.path.exists(path):
            res="Original"
        path=self.dir+"/Steam.txt"
        if os.path.exists(path):
            res="Steam"
        return res
        
        
    def find_publisher_year(self):
        path=self.dir+"/Publisher.txt"
        if os.path.exists(path):
            f=open(path)
            line=f.readline().split(";")
            f.close()
            try:
                (publisher,year)=(self.mem.publishers.find(int(line[0])),int(line[1]))
            except:
                (publisher, year)=(self.mem.publishers.find(0), -1)
            return (publisher,year)
        return (self.mem.publishers.find(0),-1)       
        
    def find_valoration(self):
        """If it is found, read the file number. If not valoration will be zero"""
        path=self.dir+"/Valoration.txt"
        res=0
        if os.path.exists(path):
            f=open(path)
            line=f.readline()
            f.close()
            try:
                res=int(line)
            except:
                pass
        return res

    def find_wished(self):
        """Can be a boolean"""
        res=False
        path=self.dir+"/Wished.txt"
        if os.path.exists(path):
            res=True
        return res
        
    def find_working(self):
        """Can be a boolean. None: not texted yet, True has run.sh, False has norun.sh"""
        res=None
        if os.path.exists(self.dir+"/run.sh"):
            res=True
        elif os.path.exists(self.dir+"/norun.sh"):
            res=False
            f=open(self.dir+"/norun.sh")
            try:
                i=int(f.readline()[0:8])
                s=str(i)
                self.norundate=datetime.date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
            except:
                pass
        return res

    def find_experience(self):
        s=""
#        path=self.dir+"/Experiencia.txt"
#        if os.path.exists(path):
#            print ("mv '{0}/{1}/Experiencia.txt' '{0}/{1}/Experience.txt'".format(os.getcwd(),self.dir ))
            
        path=self.dir+"/Experience.txt"
        if os.path.exists(path):
            f=open(path)
            for line in f.readlines():
#                
#                line=line.replace("\\","{\\textbackslash}")
#                line=line.replace("\n","\n\n")
#                line=line.replace("_","\_")
#                line=line.replace("/","\/")
#                if line[0]=="\t":
#                    line=line.replace("\t","{\\indent}")
#                else:
#                    line="{\\noindent}"+line
                s=s+line
            f.close()
        return s


    def find_languages(self):
        res=SetLanguages(self.mem)
        path=self.dir+"/Languages.txt"
        if os.path.exists(path):
            f=open(path)
            for line in f.readlines():
                line=line.replace("\n","")
                if line!="":
                    res.arr.append(self.mem.languages.find(line))
            f.close()
        return res

    def find_categories(self):
        res=SetCategories(self.mem)
        path=self.dir+"/Categories.txt"
        if os.path.exists(path):
            f=open(path)
            for line in f.readlines():
                if line!="":
                    res.arr.append(self.mem.categories.find(int(line)))
            f.close()
        return res
    def __repr__(self):
        publisher=""
        cover="No"
        if self.publisher!=None:
            publisher=self.publisher.name
        if self.cover!=None:
            cover="Yes"
        return "Game: {0}. Year: {1}. Publisher: {2}. Categories: {3}. Languages: {4}. Cover: {5}. Screenshots: {6}".format(self.title, self.year, publisher, len(self.categories.arr), len(self.languages.arr),cover,len(self.screenshots))

class SetGames:
    def __init__(self,mem):
        self.mem=mem
        self.arr=[]
    
    def load(self):
        for i, dir in enumerate(os.listdir(args.directory)):
            path=args.directory+"/"+dir
            if os.path.isdir(path) and dir not in ("Not indexed", "Unwanted"):
                self.arr.append(Game(self.mem,i,path))
        return self
    
    def sort_by_category(self):
        self.arr = sorted(self.arr, key=lambda g: (g.category.name, g.title))
    
    def sort_by_name(self):
        self.arr=sorted(self.arr, key=lambda g: g.title)
        
    def sort_by_publisher(self):
        self.arr = sorted(self.arr, key=lambda g: (g.publisher.name, g.title))
    
    def sort_by_valoration(self):
        self.arr = sorted(self.arr, key=lambda g: (g.valoration, g.title))
    
    def sort_by_year(self):
        self.arr = sorted(self.arr, key=lambda g: (g.year, g.title))
        
def string2tex(cadena):
	cadena=cadena.replace('[','$ [ $')
	cadena=cadena.replace(']','$ ] $')
	cadena=cadena.replace('&','\&')
	cadena=cadena.replace('²','$ ^2 $')
	return cadena

def help():
    print ("gamesreport [list|generate]")
    print ("  - version {0}".format(version))

def show_fields():
    print("This program generates a PDF document, reading Games from a directory with a concret structure.")
    print("Here are the details of the files can have each game:")
    print (" * Files:")
    print ("   - Title.txt: Optional")
    print ("   - Publisher.txt: Publisher;Year")
    print ("   - Cover.jpg: Cover")
    print ("   - Screenshot.1.jpg: First screenshot")
    print ("   - Categories.txt: Category")
    print ("   - Languages.txt: Language")
    print ("   - Experiencia.txt: Experiencia")
    print ("   - Steam.txt: If it's working with an Steam System")
    print ("   - Original.txt: If I have in an original device")
    print ("   - Valoration.txt: Game puntuation")
    print ("   - run.sh: If the game runs directly")
    print ("   - norun.sh: I couldn't make it work yet. It has a date YYYYMMDD format, last tested")
    print ("   - wished.txt: Wished game. I still haven't got")
    print (" * Directories:")
    print ("   - Game: Where downloaded files are (iso, exe,...)")
    print ("   - Personal: Where saves or personal configuration are saved")
    print ("   - .wine*: Where wine game directory is generated")
    
    print ("There are special directories:")
    print (" * Unwanted. It has a subdirectory for each unwanted game. Reason is added in Esperience.txt")
    print (" * Not indexed. It has a subdirectory with games I don't want to index")
    print ("")
    
    print ("Help for editing this files:")
    print (" * Categories")
    for a in mem.categories.arr:
        print ("   - {0}. {1}".format(a.id, a.name))
    print("")
    
    print (" * Languages")
    for a in mem.languages.arr:
        print ("   - {0}. {1}".format(a.id, a.name))
    print("")
    
    print (" * Publishers")
    for a in mem.publishers.arr:
        print ("   - {0}. {1}".format(a.id, a.name))
    print ("")
    
    print (" * Valoration")
    print ("   - Must be a number from 0 to 100")
    

    


### MAIN SCRIPT ###
parser=argparse.ArgumentParser(prog='gamesreport', description='My games report generator',  epilog="Developed by Mariano Muñoz 2015 ©")
parser.add_argument('-v', '--version', action='version', version="0.1.0")
group = parser.add_mutually_exclusive_group()
group.add_argument('-g',  '--generate', help='Generate report',  action='store_true')
group.add_argument('-l',  '--list', help='List information', action='store_true')
parser.add_argument('-d',  '--directory',  help="Games directory",  default=os.getcwd())
args=parser.parse_args()

if args.list:
    mem=Mem()
    mem.games.sort_by_name()
    show_fields()
    sys.exit(100)
        
if args.generate:
    print ("Searching games in {}".format(args.directory))
    mem=Mem()
    mem.games.sort_by_name()
    doc=GamesReport(mem, "GamesReport.odt", "/usr/share/gamesreport/report.odt" )
    doc.generate()

