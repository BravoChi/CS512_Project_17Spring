package dataPrepare;
import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
public class FileTrans {
	public static String inputFilePath = "bioconcepts2pubtator_offsets.txt";
	public static String inputPmid = "pmid_2012_2016.txt"; 

	
	public void prepare() throws IOException{
		long start = System.currentTimeMillis();
		long startPoint = start;
		long endPoint = start;
		FileInputStream is = new FileInputStream(inputFilePath);
		FileOutputStream os = new FileOutputStream("filePart2.txt");
		BufferedReader br = new BufferedReader(new InputStreamReader(is));
		BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(os));
		String line = br.readLine();
		int count = 1;
		int subCount = 1;
		int inRange = 0;
		
		while(line != null){
			ArrayList<String> block = new ArrayList<String>();
			while(!line.equals("") && !line.equals(null)){
				block.add(line);
				line = br.readLine();
				//System.out.println("No." + i + ": " + line.equals(""));
			}
			if(line == null){
				break;
			}
			if(block != null){
				int temp = process(block);
				if(temp >= 15705606 && temp <= 27922260){
					inRange++;
					for(int i = 0; i < block.size(); i++){
						bw.write(block.get(i) + "\n");
					}
					bw.write("\n");
				}
			}
			
			line = br.readLine();
			count++;
			
			if(count % 1000000 == 0){
				endPoint = System.currentTimeMillis();
				System.out.println(subCount + "000000, in range: " + inRange+ "; run time: " + (endPoint - startPoint) / 1000 + "s");
				System.out.println(line);
				startPoint = System.currentTimeMillis();
				subCount++;
			}
		}
		
		System.out.println("Count: " + count + "In range: " + inRange);
		long end = System.currentTimeMillis();
		System.out.println("Running Time: " + (end - start) / 1000 + "s");
		bw.close();
		br.close();
		is.close();
		os.close();
	}
	public int process(ArrayList<String> block){
		String pmid = null;
		String abs = null;
		//String title = null;
		//ArrayList<Entity> entitySet = new ArrayList<Entity>();
		//System.out.println("block Size: " + block.size());
		for(int i = 0; i < block.size(); i++){
			if(i == 0){
				String firstLine = block.get(i);
				//System.out.println(firstLine);
				String firstSplit[] = firstLine.split("\\|", 3);
				if(firstSplit[1].equals("t")){
					pmid = firstSplit[0].trim();
					//title = firstSplit[2];
				}
				//System.out.println("Pmid: " + pmid);
				//System.out.println("title: " + title);
			}
//			if(!set.contains(pmid)){
//				continue;
//			}
//			if(i == 1){
//				String secLine = block.get(i);
//				String secSplit[] = secLine.split("\\|", 3);
//				if(secSplit[1].equals("a") && secSplit[0].trim().equals(pmid)){
//					abs = secSplit[2];
//				}
//				//System.out.println("Abstract: " + abs);
//
//			}
//			String line = block.get(i);
//			String[] lineSplit = line.split("	", 6);
//			if(lineSplit[0].trim().equals(pmid)){
//				Entity e = new Entity(Integer.parseInt(lineSplit[1]), lineSplit[3], lineSplit[4], lineSplit[5]);
//				entitySet.add(e);
//			}
		}
		
//		Pmid p = new Pmid(pmid);
//		p.addEntity(entitySet);
//		System.out.println("Entity Size: " + (entitySet.size() == block.size() - 2) + "\n");
		return Integer.parseInt(pmid.trim());
	}
	public void findRange() throws IOException{
		int max = Integer.MIN_VALUE;
		int min = Integer.MAX_VALUE;
		//int secMin = Integer.MAX_VALUE;
		FileInputStream is = new FileInputStream(inputPmid);
		BufferedReader br = new BufferedReader(new InputStreamReader(is));
		String line = br.readLine();
		int count = 0;
		while(line != null){
			
			int val = Integer.parseInt(line.trim());
			if(val > max)
				max = val;
			if(val < min)
				min = val;
			if(val <= 20036095){
				System.out.println(line);
				count++;
			}
			line = br.readLine();
		}
		System.out.println(count);
		br.close();
		is.close();
		System.out.println("Range is from " + min + " to " + max);
	}
	
	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
		FileTrans ft = new FileTrans();
		ft.prepare();
		//ft.findRange();
	}

}
