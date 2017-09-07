package setSearch;
import java.io.*;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import org.bson.Document;

import com.mongodb.client.MongoCollection;
import com.mongodb.client.model.Filters;

public class Preprocessing {
	public String inputFilePath;
	public String inputPmid; 
	public String inputDate;
	public String inputAuthor;
	public String inputJournal;
	private HashSet<String> pmidSet;
	private int pmidSize;
	private int fileSize;
	private int fileMatch;
	private int entityCount;
	private HashMap<String, Integer> entityStat;
	private int dateSize;
	private int dateMatch;
	private HashMap<String, Integer> dateStat;
	private int authorSize;
	private int authorMatch;
	private int journalSize;
	private int journalMatch;
	private long duration;
	private Mongo mongoDB;
	private int insertBuckSize;
	private int updateBuckSize;
	//MongoClient mongoClient;
	//MongoDatabase db;
	//private int bioPmidMatch;
	
	public Preprocessing() throws IOException{
		long start = System.currentTimeMillis();      
		//this.pmidSet = new HashMap<String,Pmid>();
		this.pmidSet = new HashSet<String>();
		//this.inputFilePath = "bioconcepts2pubtator_offsets.txt";
		this.inputFilePath = "bioconcepts2pubtator_offsets2.txt";
		this.inputPmid = "pmid_2012_2016.txt"; 
		this.inputDate = "pmid2date.txt";
		this.inputAuthor = "pmid_author.txt";
		this.inputJournal = "pmid_journal.txt";
		this.fileSize = 0;
		this.fileMatch = 0;
		this.entityCount = 0;
		this.entityStat = new HashMap<String, Integer>();
		this.dateSize = 0;
		this.dateMatch = 0;
		this.dateStat = new HashMap<String, Integer>();
		this.authorSize = 0;
		this.authorMatch = 0;
		this.journalSize = 0;
		this.journalMatch = 0;
		this.insertBuckSize = 1000;
		this.updateBuckSize = 1000;
		this.duration = 0L;
		initialSet(this.inputPmid);
		this.mongoDB = new Mongo("PmidDB");
		long end = System.currentTimeMillis();   
		System.out.println("Successfully Initialized! The size of data is:" + this.pmidSet.size());
		System.out.println("Running Time: " + (end - start) / 1000 + "s");
	}
	
	public void initialSet(String path) throws IOException{
		FileInputStream is = new FileInputStream(path);
		BufferedReader br = new BufferedReader(new InputStreamReader(is));
		String line = br.readLine();
		while(line != null){
			pmidSet.add(line.trim());
			line = br.readLine();
		}
		br.close();
		is.close();
		System.out.println("Succesfully created pmid Set!");
	}
	
	public void addJournal() throws IOException{
		long start = System.currentTimeMillis();
		long startPoint = start, endPoint;
		FileInputStream is = new FileInputStream(inputJournal);
		BufferedReader br = new BufferedReader(new InputStreamReader(is));
		String line = br.readLine();
		ArrayList<String[]> list = new ArrayList<String[]>();
		while(line != null){
			journalSize++;
			String[] lines = line.split("	");
			if(!pmidSet.contains(lines[0])){
				line = br.readLine();
				continue;
			} else{
				journalMatch++;
				list.add(lines);
			}
			if(list.size() == updateBuckSize){
				insert('J', list);
				list = new ArrayList<String[]>();
			}
			line = br.readLine();
			if(journalSize % 10000 == 0){
				endPoint = System.currentTimeMillis();
				System.out.println(journalSize / 10000 + "0000, run time: " + (endPoint - startPoint) + "ms");
				System.out.println(line);
				startPoint = System.currentTimeMillis();
			}
		}
		if(!list.isEmpty()){
			insert('J', list);
		}
		br.close();
		is.close();
		long end = System.currentTimeMillis();
		System.out.println("Journal added, total lines: " + journalSize + "; " + journalMatch + " of them matched");
		System.out.println("Running Time: " + (end - start) / 1000 + "s");
	}
	public void addAuthor() throws IOException{
		System.out.println("Start add Author!!");
		long start = System.currentTimeMillis();
		long startPoint = start, endPoint = start;
		FileInputStream is = new FileInputStream(inputAuthor);
		BufferedReader br = new BufferedReader(new InputStreamReader(is));
		String line = br.readLine();
		ArrayList<String[]> list = new ArrayList<String[]>();
		while(line != null){
			authorSize++;
			String[] lines = line.split("	");
			if(!pmidSet.contains(lines[0]) || lines.length != 2){
				line = br.readLine();
				continue;
			} else{
				list.add(lines);
				authorMatch++;
			}
			if(list.size() == updateBuckSize){
				insert('A', list);
				list = new ArrayList<String[]>();
			}
			line = br.readLine();
			if(authorSize % 10000 == 0){
				endPoint = System.currentTimeMillis();
				System.out.println(authorSize / 10000 + "0000, run time: " + (endPoint - startPoint) + "ms");
				System.out.println(line);
				startPoint = System.currentTimeMillis();
			}
		}
		if(!list.isEmpty()){
			insert('A', list);
		}
		br.close();
		is.close();
		long end = System.currentTimeMillis();
		System.out.println("Author added, total lines: " + authorSize + "; " + authorMatch + " of them matched");
		System.out.println("Running Time: " + (end - start) / 1000 + "s");
	}
	public void addDate() throws IOException{
		long start = System.currentTimeMillis();
		long startPoint = start, endPoint = start;
		FileInputStream is = new FileInputStream(inputDate);
		BufferedReader br = new BufferedReader(new InputStreamReader(is));
		String line = br.readLine();
		ArrayList<String[]> list = new ArrayList<String[]>();
		//int total = 0, matched = 0;
		while(line != null){
			dateSize++;
			String[] lines = line.split("	");
			if(!pmidSet.contains(lines[0])){
				line = br.readLine();
				continue;
			} else{
				list.add(lines);
				dateStat.put(lines[1], dateStat.getOrDefault(lines[1], 0) + 1);
				dateMatch++;
			}
			if(list.size() == updateBuckSize){
				insert('D', list);
				list = new ArrayList<String[]>();
			}
			line = br.readLine();
			if(dateSize % 10000 == 0){
				endPoint = System.currentTimeMillis();
				System.out.println(dateSize / 10000 + "0000, run time: " + (endPoint - startPoint) + "ms");
				System.out.println(line);
				startPoint = System.currentTimeMillis();
			}
		}
		if(!list.isEmpty()){
			insert('D', list);
		}
		br.close();
		is.close();
		long end = System.currentTimeMillis();
		System.out.println("Date added, total lines: " + dateSize + "; " + dateMatch + " of them matched");
		System.out.println("Running Time: " + (end - start) / 1000 + "s");
	}
	public void fileInput() throws IOException{
		long start = System.currentTimeMillis();
		long startPoint = start;
		long endPoint = start;
		ArrayList<Document> list = new ArrayList<Document>();
		FileInputStream is = new FileInputStream(inputFilePath);
		BufferedReader br = new BufferedReader(new InputStreamReader(is), 50*1024*1024);
		String line = br.readLine();
		fileSize = 0;
		
		while(line != null){
			ArrayList<String> block = new ArrayList<String>();
			while(!line.equals("") && !line.equals(null)){
				block.add(line);
				line = br.readLine();
			}
			if(line == null){
				break;
			}
			if(block != null){
				Document doc = process(block);
				if(doc != null){
					list.add(doc);
					
					fileMatch++;
				}
				if(list.size() == insertBuckSize){
					writeDB(list);
					list = new ArrayList<Document>();
				}
			}
			line = br.readLine();
			fileSize++;
			if(fileSize % 1000000 == 0){
				endPoint = System.currentTimeMillis();
				System.out.println(fileSize / 1000000 + "000000, run time: " + (endPoint - startPoint) / 1000 + "s");
				System.out.println(line);
				startPoint = System.currentTimeMillis();
			}
		}
		if(!list.isEmpty()){
			writeDB(list);
		}
		System.out.println("Data Count: " + fileSize + "; Matched: " + fileMatch);
		long end = System.currentTimeMillis();
		duration = end - start;
		System.out.println("Running Time: " + duration / 1000 + "s");
		br.close();
		is.close();
		mongoDB.buildIndex("pmid");
	}
	
	public Document process(ArrayList<String> block){
		String pmid = null;
		String abs = null;
		String title = null;
		ArrayList<Document> entitySet = new ArrayList<Document>();
		for(int i = 0; i < block.size(); i++){
			if(i == 0){
				String firstLine = block.get(i);
				String firstSplit[] = firstLine.split("\\|", 3);
				if(firstSplit[1].equals("t")){
					pmid = firstSplit[0].trim();
					title = firstSplit[2];
				}
			}
			if(!pmidSet.contains(pmid)){
				return null;
			}
			if(i == 1){
				String secLine = block.get(i);
				String secSplit[] = secLine.split("\\|", 3);
				if(secSplit[1].equals("a") && secSplit[0].trim().equals(pmid)){
					abs = secSplit[2];
				}
			}
			String line = block.get(i);
			String[] lineSplit = line.split("	", 6);
			if(lineSplit[0].trim().equals(pmid)){
				entityCount++;
				entityStat.put(lineSplit[3], entityStat.getOrDefault(lineSplit[3], 0) + 1);
				Document entityDoc = new Document()
						.append("start", lineSplit[1])
						.append("end", lineSplit[2])
						.append("name", lineSplit[3])
						.append("type", lineSplit[4])
						.append("source", lineSplit[5]);
				entitySet.add(entityDoc);
			}
		}
		Document doc = new Document("pmid", pmid)
				.append("entities", entitySet)
				.append("title", title)
				.append("abstract", abs)
				.append("author", "..................................................................................................................")
				.append("journal", "............................................................................")
				.append("date", ".......");
		return doc;
	}
	public void writeDB(ArrayList<Document> list){
	    MongoCollection<Document> collection = mongoDB.getCollection("pmidCollection");
	    collection.insertMany(list);
	}
	public void insert(char type, ArrayList<String[]> list){
	    MongoCollection<Document> collection = mongoDB.getCollection("pmidCollection");
	    if(type == 'A'){
	    	for(String[] s: list){
	    		collection.updateOne(Filters.eq("pmid", s[0]), new Document("$set",new Document("author", s[1])));
	    	}
	    }
	    if(type == 'D'){
	    	for(String[] s: list){
	    		collection.updateOne(Filters.eq("pmid", s[0]), new Document("$set",new Document("date", s[1])));
	    	}
	    }
	    if(type == 'J'){
	    	for(String[] s: list){
		    	collection.updateOne(Filters.eq("pmid", s[0]), new Document("$set",new Document("journal", s[1])));
	    	}
	    }
	}
	public void summary(String path) throws IOException{
		FileOutputStream os = new FileOutputStream(path);
		BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(os));
		Date now = new Date(); 
		DateFormat df = DateFormat.getDateInstance();
	    String date = df.format(now);
		bw.write("Author: Wenzhuang CHI, Generated Date: " + date);
		bw.write("Dataset Rebuild Successfully, Consumed " + duration + "s! \n");
		bw.write("Totally there are " + pmidSize + " records in the file" + inputPmid + ", and these records have been rebuild and stored in MongoDB.\n");
		bw.write("Among those records, there are totally " + entityCount + " entities, in average, " + (float)entityCount / (float)pmidSize + " for each record.\n");
		bw.write("For the file " + inputFilePath + ", there are " + fileSize + " records inside, and " + fileMatch + "of them matched with " + inputPmid + "\n");
		bw.write("For the file " + inputDate + ", there are " + dateSize + " records inside, and " + dateMatch + "of them matched with " + inputPmid + "\n");
		bw.write("For the file " + inputAuthor + ", there are " + authorSize + " records inside, and " + authorMatch + "of them matched with " + inputPmid + "\n");
		bw.write("For the file " + inputJournal + ", there are " + journalSize + " records inside, and " + journalMatch + "of them matched with " + inputPmid + "\n");
		bw.write("Detail of Date count shown as blow: \n");
		for(String s: dateStat.keySet()){
			bw.write(s + ": " + dateStat.get(s) + "\n");
		}
		bw.write("Detail of enetity count shown as blow: \n");
		for(String s: entityStat.keySet()){
			bw.write(s + ": " + entityStat.get(s) + "\n");
		}
		bw.close();
		os.close();
	}
	public void rebuild(String path) throws IOException{
		fileInput();
		addAuthor();
		addDate();
		addJournal();
		summary(path);
	}
	public void test(String path) throws IOException{
		FileInputStream is = new FileInputStream(path);
		BufferedReader br = new BufferedReader(new InputStreamReader(is), 50*1024*1024);
		String line = br.readLine();
		int count = 1;
		while(line != null && count < 10){
			count++;
			line = br.readLine();
			System.out.println(line);
		}
		br.close();
		is.close();
	}
	public static void main(String[] args) throws IOException, InterruptedException {
		Preprocessing pp = new Preprocessing();
		//pp.test("bioconcepts2pubtator_offsets2.txt");
		pp.rebuild("DatasetSummary.txt");
		
	}

}
