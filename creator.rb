require 'find'

# Define the directory path you want to search for PDF files
directory_path = 'C:/Users/amant/Documents/GitHub/voltseon.com/leerjaar-1'

# Initialize a hash to keep track of grouped PDFs
pdf_groups = {}

# Iterate through the directory to find PDF files
Find.find(directory_path) do |path|
  if File.file?(path) && File.extname(path).casecmp('.pdf') == 0
    filename = File.basename(path)
    starting_characters = filename.split(' ').first(12)[0]

    # Group PDFs with the same starting characters
    if pdf_groups.key?(starting_characters)
      pdf_groups[starting_characters] << filename
    else
      pdf_groups[starting_characters] = [filename]
    end
  end
end

# Create a text file with the formatted links
output_file = File.new('pdf_links.txt', 'w')

pdf_groups.each do |key, pdf_list|
  addon = ""
  addon << "<a href=\"pdf-viewer.html?"
  pdf_list.each_with_index do |pdf, index|
    title = pdf.split('.').first
    path = directory_path + "/#{pdf}"

    addon << "pdfTitle#{index + 1}=#{title}&pdfPath#{index + 1}=#{path}#{pdf_list.length - 1 == index ? '' : '&'}"
  end
  output_file.puts(addon + "\"")
end

output_file.close
puts 'PDF links have been generated and saved to pdf_links.txt'
