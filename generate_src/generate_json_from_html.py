# Dependency:
# pip install beautifulsoup4
from bs4 import BeautifulSoup
from pathlib import Path

# Link Object for storing extra information besides the URL
# (extra text, unit ID/Day #)
class LinkObject:
  def __init__(self, link, extra_text, unit_id):
    self.link = link
    self.extra_text = extra_text
    self.unit_id = unit_id
  def __str__(self):
    return f"\"link\": \"{self.link}\", \"extra\": \"{self.extra_text}\", \"unitid\": \"{self.unit_id}\""

# html "soup" -> dictionary
def html_to_dict(dict, soup):
  # Find all unordered-lists
  uls = soup.find_all('ul')
  for ul in uls:
    # get the id (if there is one)
    unitday = ul.get('id')
    if unitday:
      # okay, there's an id which means we are in a list with text + links for a powerpoint slide
      # debug:
      print("[= Unit " + unitday + " =] parsing...")
      # get all the list items
      lis = ul.find_all('li')
      for li in lis:
        # li includes the text and the hyperlink
        #print(li.text)
        # the 'anchor' includes the hyperlink and text
        anchor = li.find('a')
        if anchor:
          link = anchor.get('href')
          link_text = li.text.strip()   # anchor.text is just what's captured between <a> tags    
          link_extra_text = ""
          # All UPPERCASE keys for ASL dictionary (might need to manually fix links with multiple definitions)
          a_text = anchor.text.strip().upper()
          if (len(a_text) != len(link_text)):
            link_extra_text = link_text[len(a_text):].strip()
            #print("<->" + link_extra_text)

          # putting it all together:
          print(unitday + ": " + link_text + ": URL: " + link + ", extra_text: " + link_extra_text)

          link_obj = LinkObject(link, link_extra_text, unitday)
          lesson_addition = True
          if (unitday[-1] == "x"):
            lesson_addition = False

          # Already added word?
          if (a_text in dict):
            # mismatch: If True, ignore or fixup. False - ignore
            mismatch = False

            # link not the same??            
            if (dict[a_text].link != link):
              #print("Mismatch for key " + a_text + " in dictionary, prev link: " + dict[a_text] + ", new link: " + link)
              print("** " + unitday + " Mismatch link in key " + a_text + " in dictionary, 1st unit/day: " + dict[a_text].unit_id + ", prev link: " + dict[a_text].link + ", new link: " + link_obj.link)
              # keeping previous link for now..
              mismatch = True
            if (dict[a_text].extra_text.upper() != link_extra_text.upper()):
              print("*+ " + unitday + " Mismatch extra_text in key " + a_text + ": prev extra_text: " + dict[a_text].extra_text + ", new extra: " + link_extra_text)
              if (len(dict[a_text].extra_text) < len(link_extra_text)):
                dict[a_text].extra_text = link_extra_text
              mismatch = True
            # Future-proof for manually added word/links: if previous find WAS manually entered but current isn't
            if (lesson_addition and (dict[a_text].unit_id[-1] == "x")):
              print("x-- Dupe of manually-added link with lesson-added link, previous unit/day: " + dict[a_text].unit_id + ", current: " + unitday)
              # set to unit/day where it appears
              dict[a_text].unit_id = unitday
              mismatch = True
            # No differences found? Pure duplicate
            if (not mismatch):
              print("  ++ Dupe #x of " + a_text + ", 1st unit/day: " + dict[a_text].unit_id  + ", new: " + unitday)
          else:
            # Check for spaces (more thoroughly could check for ALL whitespace...)
            if (a_text.find(' ') == -1):
              dict[a_text] = link_obj
            else:
              print("!! anchor '" + a_text + "' contains whitespace, not adding")
          #print(anchor.text)

  #print(ul)

# -- html_to_dict()

dict = {}

# Opening the html file 
#HTMLFile = open("output.html", "r") 
# Reading the file 
#index = HTMLFile.read()
# Creating a BeautifulSoup object and specifying the parser 
#soup = BeautifulSoup(index, 'lxml') 

#html_to_dict(dict, soup)

# directory name
dirname = '.'
# giving directory name to Path() function
paths = Path(dirname).glob('**/*.html',)
 
# iterating over all files
for path in paths:
  print(" -- PARSING -- " + str(path))
  HTMLFile = open(str(path), "r")
  index = HTMLFile.read()
  # Creating a BeautifulSoup object and specifying the parser 
  soup = BeautifulSoup(index, 'lxml')  
  html_to_dict(dict, soup)


#print(dict)
# Printing a dictionary using a loop and the items() method
#for key, value in dict.items():
#  print(key, ":", value)

file = open("output.json", "w", encoding="utf-8")
file.write("{\"items\": [\n")
str_blob = ""
print("\n====  JSON OUTPUT ====\n")
for key, value in dict.items():
  print(key, ":", value)
  str_blob += "\t{\"text\": \"" + key.strip() + "\", " + value.__str__() + "},\n"

# remove ",\n", add back "\n"
str_blob = str_blob[:-2] + "\n"
file.write(str_blob)
file.write("]}\n")
file.close()
