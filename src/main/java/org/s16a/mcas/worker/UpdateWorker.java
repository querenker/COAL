package org.s16a.mcas.worker;

import com.clarifai.api.ClarifaiClient;
import com.clarifai.api.RecognitionRequest;
import com.clarifai.api.RecognitionResult;
import com.clarifai.api.Tag;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Resource;
import org.s16a.mcas.Hasher;
import org.s16a.mcas.MCAS;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.ThreadFactory;

/**
 * Created by aloeser on 25.05.16.
 */
public class UpdateWorker extends AbstractWorker {

    public UpdateWorker() {
        super("update");
    }

    @Override
    protected void processData(String filename) throws IOException {
        String originalFile = filename.substring(0, filename.lastIndexOf('.'));
        Model model = openModel(originalFile);
        Model newPart = openModel(filename);
        model.add(newPart);
        writeModel(model, originalFile);
    }

    public static void main(String[] args) throws Exception {
        AbstractWorker.startWorker(new UpdateWorker());
    }
}
