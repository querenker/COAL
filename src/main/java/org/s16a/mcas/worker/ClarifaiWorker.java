package org.s16a.mcas.worker;

import com.clarifai.api.ClarifaiClient;
import com.clarifai.api.RecognitionRequest;
import com.clarifai.api.RecognitionResult;
import com.clarifai.api.Tag;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Resource;
import com.rabbitmq.client.*;
import org.s16a.mcas.Hasher;
import org.s16a.mcas.MCAS;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

public class ClarifaiWorker extends AbstractWorker {

    public ClarifaiWorker() {
        super(MCAS.clarifai);
    }

    @Override
    protected void processData(String url) throws IOException {
        // open model
        String modelFileName = Hasher.getCacheFilename(url);
        try { Thread.sleep(5000); } catch (InterruptedException ie) {}
        Model model = openModel(modelFileName);
        String dataFileName = Hasher.getCacheFilename(url) + ".data";

        ClarifaiClient clarifai = new ClarifaiClient("T1p6TiGA5ybz8KkaWQmAR26kwWQRcUYV2d1LFVsl", "MpvrBCyR7XgeOPaKsXbBCaH_RbWitmKzBtPqD9Et");
        List<RecognitionResult> results = clarifai.recognize(new RecognitionRequest(url));

        Resource r = model.createResource();
        for (Tag tag : results.get(0).getTags()) {
            System.out.println(tag.getName() + ": " + tag.getProbability());
            r.addLiteral(model.createProperty("http://ogp.mme/ns#tag:" + tag.getName()), tag.getProbability());
        }
        model.getResource(url).addProperty(MCAS.clarifai, r);

        writeModel(model, modelFileName);
    }

    public static void main(String[] args) throws Exception {
        AbstractWorker.startWorker(new ClarifaiWorker());
    }
}
/*
public class ClarifaiWorker {

    private static final String TASK_QUEUE_NAME = MCAS.clarifai.toString();

    public static void main(String[] argv) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        final Connection connection = factory.newConnection();
        final Channel channel = connection.createChannel();

        channel.queueDeclare(TASK_QUEUE_NAME, true, false, false, null);
        System.out.println(" [*] Waiting for messages. To exit press CTRL+C");

        channel.basicQos(1);

        final Consumer consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                String message = new String(body, "UTF-8");

                System.out.println(" [x] Received '" + message + "'");
                try {
                    extractClarifaiInfo(message);
                } finally {
                    System.out.println(" [x] Done");
                    channel.basicAck(envelope.getDeliveryTag(), false);
                }
            }
        };
        channel.basicConsume(TASK_QUEUE_NAME, false, consumer);
    }

    private static void extractClarifaiInfo(String url) throws IOException {


    }
}
//*/
