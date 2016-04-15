package org.s16a.mcas;

import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class Hasher {

	public static String hash(String input) {
		MessageDigest m = null;
		try {
			m = MessageDigest.getInstance("MD5");
		} catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
		m.update(input.getBytes(), 0, input.length());
		return new BigInteger(1, m.digest()).toString(16);
	}

	private static String BASE_PATH = "cache/";

	private static String BASE_EXT = ".ttl";
	
	public static String getCacheFilename(String input){
		return BASE_PATH + hash(input) + BASE_EXT;
	}
}
