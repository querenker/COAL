package org.s16a.mcas.worker;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.DC;
import com.rabbitmq.client.*;
import org.s16a.mcas.Enqueuer;
import org.s16a.mcas.Hasher;
import org.s16a.mcas.MCAS;
import org.s16a.mcas.util.MediaInfo;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;

/**
 * Created by aloeser on 19.05.16.
 */
public abstract class AbstractWorker {

    public final String TASK_QUEUE_NAME;

    public AbstractWorker(Property property) {
        this(property.toString());
    }

    public AbstractWorker(String queueName) {
        TASK_QUEUE_NAME = queueName;
    }


    public static void startWorker(final AbstractWorker worker) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        final Connection connection = factory.newConnection();
        final Channel channel = connection.createChannel();


        channel.queueDeclare(worker.TASK_QUEUE_NAME, true, false, false, null);
        System.out.println(" [*] Waiting for messages. To exit press CTRL+C");

        channel.basicQos(1);

        final Consumer consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                String message = new String(body, "UTF-8");

                System.out.println(" [x] Received '" + message + "'");
                try {
                    worker.processData(message); //usually URL
                } finally {
                    System.out.println(" [x] Done");
                    channel.basicAck(envelope.getDeliveryTag(), false);
                }
            }
        };
        channel.basicConsume(worker.TASK_QUEUE_NAME, false, consumer);
    }

    public Model getNewModel() {
        return ModelFactory.createDefaultModel();
    }

    public Model openModel(String modelFileName) {
        Model model = ModelFactory.createDefaultModel();
        File f = new File(modelFileName);

        if (f.exists()) {
            model.read(modelFileName, "TURTLE");
        }

        return model;
    }

    public void writeModel(Model model, String modelFileName) throws IOException {
        FileWriter out = new FileWriter(modelFileName);
        try {
            model.write(out, "TURTLE");
        } finally {
            try {
                out.close();
            } catch (IOException closeException) {
                // ignore
            }
        }
    }

    public void writeAndMergeModel(Model model, String modelFileName) throws IOException {
        writeModel(model, modelFileName);
        try {
            notifyUpdater(modelFileName);
        } catch (IOException ioe) {
            throw ioe;
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(42);
        }
    }

    public void notifyUpdater(String filename) throws Exception {
        Enqueuer.enqueueForMerge(filename);
    }

    public String getModelFileName(String url) {
        return Hasher.getCacheFilename(url) + "." + TASK_QUEUE_NAME.substring(TASK_QUEUE_NAME.lastIndexOf('/')+1);
    }

    protected abstract void processData(String url) throws IOException;
}