package org.s16a.mcas;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class MCAS {
    /** <p>The RDF model that holds the vocabulary terms</p> */
    private static Model m_model = ModelFactory.createDefaultModel();
    
    /** <p>The namespace of the vocabalary as a string ({@value})</p> */
    public static final String NS = "http://s16a.org/vocab/mcas/1.0/";
    
    /** <p>The namespace of the vocabalary as a string</p>
     *  @see #NS */
    public static String getURI() {return NS;}
    
    /** <p>The namespace of the vocabalary as a resource</p> */
    public static final Resource NAMESPACE = m_model.createResource( NS );
    
    public static final Property mediainfo = m_model.createProperty( NS + "mediainfo" );
    public static final Property vcd = m_model.createProperty(  NS + "vcd" );    
    public static final Property ner = m_model.createProperty(  NS + "ner" );
    public static final Property clarifai = m_model.createProperty( NS + "clarifai" );
    
}