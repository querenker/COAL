package org.s16a.mcas.worker;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.s16a.mcas.Hasher;
import org.s16a.mcas.MCAS;
import org.s16a.mcas.util.MediaInfo;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.DC;
import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;

public class MediainfoWorker extends AbstractWorker {

	public MediainfoWorker() {
		super(MCAS.mediainfo);
	}

	public static void main(String[] args) throws Exception {
		AbstractWorker.startWorker(new MediainfoWorker());
	}

	@Override
	protected void processData(String url) throws IOException { //ganz dreist aus extractMediainfo() kopiert
		// open model
		String modelFileName = Hasher.getCacheFilename(url);
		Model model = openModel(modelFileName);

		String dataFileName = Hasher.getCacheFilename(url) + ".data";

		MediaInfo info = new MediaInfo();
		info.open(new File(dataFileName));

		String format = info.get(MediaInfo.StreamKind.Image, 0, "Format", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);
		String width = info.get(MediaInfo.StreamKind.Image, 0, "Width", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);
		String height = info.get(MediaInfo.StreamKind.Image, 0, "Height", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);
		String bits = info.get(MediaInfo.StreamKind.Image, 0, "Bit depth", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);
		String compressionMode = info.get(MediaInfo.StreamKind.Image, 0, "Compression mode", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);

		// Format : PNG
		// Format/Info : Portable Network Graphic
		// File size : 133 KiB
		//
		// Image
		// Format : PNG
		// Format/Info : Portable Network Graphic
		// Width : 954 pixels
		// Height : 503 pixels
		// Bit depth : 32 bits
		// Compression mode : Lossless
		// Stream size : 133 KiB (100%)

		Resource r = model.createResource();
		r.addLiteral(DC.format, format);
		r.addLiteral(model.createProperty("http://ogp.me/ns#image:height"), height);
		r.addLiteral(model.createProperty("http://ogp.me/ns#image:width"), width);
		model.getResource(url).addProperty(MCAS.mediainfo, r);

		writeModel(model, modelFileName);
	}
}