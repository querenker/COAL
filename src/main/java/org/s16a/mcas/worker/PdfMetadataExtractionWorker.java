package org.s16a.mcas.worker;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Resource;
import com.rabbitmq.client.*;
import org.s16a.mcas.Hasher;
import org.s16a.mcas.MCAS;

import java.io.*;
import java.util.List;

public class PdfMetadataExtractionWorker extends AbstractWorker {

    public PdfMetadataExtractionWorker() {
        super(MCAS.pdfmetadataextraction);
    }

    @Override
    protected void processData(String url) throws IOException {
        // open model
        String modelFileName = Hasher.getCacheFilename(url);
        Model model = openModel(modelFileName);
        String dataFileName = Hasher.getCacheFilename(url) + ".data";

        Resource r = model.createResource();
        /*for (Tag tag : results.get(0).getTags()) {
            System.out.println(tag.getName() + ": " + tag.getProbability());
            r.addLiteral(model.createProperty("http://ogp.mme/ns#tag:" + tag.getName()), tag.getProbability());
        }*/
        model.getResource(url).addProperty(MCAS.pdfmetadataextraction, r);

        System.out.println(new File(".").getAbsolutePath());

        Process p = Runtime.getRuntime().exec("./pdfMetadataExtraction/pdfMetadataExtraction.py " + dataFileName);

        BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String key;
        while((key = in.readLine()) != null) {
            String value = in.readLine();
            r.addLiteral(model.createProperty("http://ogp.mme/ns#pdfmeta:" + key), value);
        }


        writeModel(model, modelFileName);
    }

    public static void main(String[] args) throws Exception {
        AbstractWorker.startWorker(new PdfMetadataExtractionWorker());
    }
}