package org.s16a.mcas;

import java.io.File;

import org.junit.Test;
import org.s16a.mcas.util.MediaInfo;


public class MediainfoTest {

	@Test
	public void test() {
		// pls copy  lib/libmediainfo.dylib   to  /usr/local/lib
		
		MediaInfo info = new MediaInfo();
		info.open(new File(""));

		String frameRate = info.get(MediaInfo.StreamKind.Video, 0, "FrameRate", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);
		String frameCount = info.get(MediaInfo.StreamKind.Video, 0, "FrameCount", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);
		String duration = info.get(MediaInfo.StreamKind.Video, 0, "Duration", MediaInfo.InfoKind.Text, MediaInfo.InfoKind.Name);
		
//		Format                                   : PNG
//		Format/Info                              : Portable Network Graphic
//		File size                                : 133 KiB
//
//		Image
//		Format                                   : PNG
//		Format/Info                              : Portable Network Graphic
//		Width                                    : 954 pixels
//		Height                                   : 503 pixels
//		Bit depth                                : 32 bits
//		Compression mode                         : Lossless
//		Stream size                              : 133 KiB (100%)
		
		System.out.println(frameCount);
	}

}
